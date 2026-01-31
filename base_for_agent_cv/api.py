#!/usr/bin/env python3
"""
CZ Career Architect — FastAPI Backend v2.0.0
Model: gpt-5.2 | Chat-first interaction mode
"""
import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Load environment
ROOT_DIR = Path(__file__).resolve().parent
env_path = ROOT_DIR / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            os.environ[key] = val

from agents import Agent, Runner, ModelSettings

import sys
sys.path.insert(0, str(ROOT_DIR / 'packages'))
from validators.cz_cv_validator_adapter import check_gdpr, check_csn_typography

# ============================================================================
# Configuration
# ============================================================================

VERSION = '2.0.0'
UPLOAD_DIR = ROOT_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}

# ============================================================================
# SYSTEM PROMPT v2.0.0 — Chat-first, RAG-mandatory
# ============================================================================

SYSTEM_PROMPT = '''You are "CZ Career Architect" — an AI assistant helping medical professionals relocating to Czech Republic.

## WHAT YOU DO
1. Create GDPR-conscious, ATS-compatible CV/životopis
2. Write Czech healthcare cover letters (motivační dopis)
3. Draft HR emails (follow-up, reference requests)
4. Guide on medical credentials: nostrifikace, aprobace, ČSK/ČLK registration
5. Provide compliance guidance: GDPR, Zákoník práce, Zákon 198/2009 Sb.

## HOW YOU COMMUNICATE
- Chat naturally in user's language (Russian/English/Czech)
- Ask minimum questions if info is missing
- Mark assumptions clearly
- Be direct, helpful, structured

## GDPR RULES (ALWAYS APPLY)

**BLOCKED — never include:**
- Birth date, age, rodné číslo
- Photo, marital status, children
- Nationality, ethnicity, religion
- Full address (only city + country)
- Reference contact details

**ALLOWED:**
- Name (title MUDr./MDDr. ONLY if Plně aprobován)
- City + country
- Email, phone (+420 xxx xxx xxx)
- Work permit status
- Nostrifikace status (with č.j.)
- "Reference k dispozici na vyžádání"

If user provides blocked data:
⚠️ GDPR: [field] — nelze zahrnout. Důvod: [reason]. Řešení: [alternative].

## ATS RULES
- No tables, columns, graphics, icons
- Linear structure, Calibri 11pt, A4
- Single language (cs-CZ default)
- 1-2 pages max

## TYPOGRAPHY — ČSN 01 6910
- Dates: 15. 1. 2025 (spaces after dots)
- Phone: +420 777 123 456
- Numbers: 25 000 Kč (space as thousands separator)

## MEDICAL CREDENTIALS
nostrifikace_status: CZ absolvent | EU uznání | Nostrifikace dokončena | V procesu | Bez nostrifikace
approbation_status: Neaprobován | V procesu | Povolení k výkonu | Písemná splněna | Ústní splněna | Plně aprobován
chamber: ČSK (dentists) | ČLK (physicians) | ČLnK (pharmacists)

## DOCUMENT LANGUAGE
- Default: Czech (cs-CZ)
- English: ONLY if user explicitly requests for international employer
- Never mix languages in document body

## WHEN GENERATING DOCUMENTS
1. Collect/infer: purpose, position, employer, credentials, experience
2. Apply profile: HR-REVIEW (default) or MEDICAL-SENIOR-EU
3. Generate document in Czech
4. Validate: GDPR + ATS + Typography
5. Return document + brief compliance note

## STYLE
- With Russian speakers: explain in Russian, documents in Czech
- Be friendly but professional
- Offer next steps proactively
- If uncertain: ask clarifying question
'''

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title='CZ Career Architect API',
    version=VERSION,
    description='Chat-first AI for Czech healthcare HR documents'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

FRONTEND_DIR = ROOT_DIR / 'frontend'
if FRONTEND_DIR.exists():
    app.mount('/static', StaticFiles(directory=FRONTEND_DIR), name='static')

# ============================================================================
# Storage
# ============================================================================

uploaded_files: dict[str, dict] = {}
chat_sessions: dict[str, list] = {}

# ============================================================================
# Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    file_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggestions: Optional[List[str]] = None

class FileInfo(BaseModel):
    id: str
    name: str
    size: int
    type: str
    uploaded_at: str
    preview: Optional[str] = None
    issues: Optional[List[str]] = None

# ============================================================================
# File Processing
# ============================================================================

def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    
    if suffix == '.txt':
        return file_path.read_text(encoding='utf-8', errors='ignore')
    
    elif suffix == '.pdf':
        try:
            import fitz
            doc = fitz.open(file_path)
            text = '\n'.join([page.get_text() for page in doc])
            doc.close()
            return text
        except:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    return '\n'.join([p.extract_text() or '' for p in pdf.pages])
            except:
                return '[Не удалось прочитать PDF]'
    
    elif suffix in {'.docx', '.doc'}:
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs])
        except:
            return '[Не удалось прочитать DOCX]'
    
    return '[Неподдерживаемый формат]'

def analyze_text(text: str) -> List[str]:
    issues = []
    findings = check_gdpr(text) + check_csn_typography(text, check_nbsp=False)
    
    for f in findings:
        if 'BIRTH' in f.code or 'AGE' in f.code:
            issues.append('❌ Дата рождения/возраст — удалить')
        elif 'MARITAL' in f.code or 'CHILD' in f.code:
            issues.append('❌ Семейный статус — удалить')
        elif 'PHOTO' in f.code:
            issues.append('❌ Фото — удалить')
        elif 'DATE' in f.code:
            issues.append('⚠️ Формат даты: 15. 1. 2025')
        elif 'PHONE' in f.code:
            issues.append('⚠️ Телефон: +420 xxx xxx xxx')
    
    return list(set(issues))[:5]

# ============================================================================
# Agent
# ============================================================================

def create_agent() -> Agent:
    return Agent(
        name='CZ Career Architect',
        instructions=SYSTEM_PROMPT,
        model=os.getenv('OPENAI_MODEL', 'gpt-5.2'),
        model_settings=ModelSettings()
    )

async def chat_with_agent(
    message: str, 
    history: List[dict] = None,
    file_context: str = None
) -> str:
    agent = create_agent()
    
    parts = []
    
    # Add conversation history (last 10 messages)
    if history and len(history) > 0:
        recent = history[-10:]
        parts.append('=== ИСТОРИЯ ДИАЛОГА ===')
        for msg in recent:
            role = 'User' if msg['role'] == 'user' else 'Assistant'
            parts.append(f'{role}: {msg["content"][:300]}')
        parts.append('=== КОНЕЦ ИСТОРИИ ===\n')
    
    # Add file context
    if file_context:
        parts.append('=== ЗАГРУЖЕННЫЙ ДОКУМЕНТ ===')
        parts.append(file_context[:4000])
        parts.append('=== КОНЕЦ ДОКУМЕНТА ===\n')
    
    # Current message
    parts.append(f'Сообщение пользователя: {message}')
    
    full_prompt = '\n'.join(parts)
    
    result = await Runner.run(agent, full_prompt)
    return str(result.final_output)

def get_suggestions(message: str) -> List[str]:
    msg = message.lower()
    
    if 'cv' in msg or 'резюме' in msg:
        return ['Добавь мотивационное письмо', 'Проверь на GDPR', 'Экспорт в DOCX']
    elif 'письмо' in msg or 'motiv' in msg:
        return ['Сделай короче', 'Добавь про опыт', 'Проверь текст']
    elif 'провер' in msg or 'check' in msg:
        return ['Исправь ошибки', 'Создай новую версию']
    elif 'ностриф' in msg or 'апроб' in msg:
        return ['Какие документы нужны?', 'Сколько занимает?']
    else:
        return ['Создай CV', 'Напиши письмо', 'Что по GDPR?']

# ============================================================================
# Endpoints
# ============================================================================

@app.get('/')
async def root():
    if (FRONTEND_DIR / 'index.html').exists():
        return FileResponse(FRONTEND_DIR / 'index.html')
    return {'message': 'CZ Career Architect API v2.0.0', 'docs': '/docs'}

@app.get('/health')
async def health():
    return {
        'status': 'online',
        'version': VERSION,
        'model': os.getenv('OPENAI_MODEL', 'gpt-5.2')
    }

@app.post('/upload', response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, 'Формат не поддерживается. Разрешены: PDF, DOCX, TXT')
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, 'Файл > 10 МБ')
    
    file_id = hashlib.md5(content).hexdigest()[:8] + '_' + str(uuid.uuid4())[:4]
    file_path = UPLOAD_DIR / f'{file_id}{suffix}'
    file_path.write_bytes(content)
    
    text = extract_text(file_path)
    issues = analyze_text(text)
    preview = text[:300] + '...' if len(text) > 300 else text
    
    file_info = {
        'id': file_id,
        'name': file.filename,
        'size': len(content),
        'type': suffix[1:],
        'path': str(file_path),
        'text': text,
        'uploaded_at': datetime.now().isoformat(),
        'preview': preview,
        'issues': issues
    }
    uploaded_files[file_id] = file_info
    
    return FileInfo(**{k: v for k, v in file_info.items() if k not in ['path', 'text']})

@app.get('/files')
async def list_files():
    return [
        FileInfo(id=f['id'], name=f['name'], size=f['size'], type=f['type'],
                 uploaded_at=f['uploaded_at'], preview=f.get('preview'), issues=f.get('issues'))
        for f in uploaded_files.values()
    ]

@app.delete('/files/{file_id}')
async def delete_file(file_id: str):
    if file_id not in uploaded_files:
        raise HTTPException(404, 'Файл не найден')
    Path(uploaded_files[file_id]['path']).unlink(missing_ok=True)
    del uploaded_files[file_id]
    return {'status': 'deleted'}

@app.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    history = chat_sessions[session_id]
    
    # File context
    file_context = None
    if request.file_ids:
        contexts = []
        for fid in request.file_ids:
            if fid in uploaded_files:
                f = uploaded_files[fid]
                contexts.append(f"Файл '{f['name']}':\n{f['text'][:2500]}")
        if contexts:
            file_context = '\n\n'.join(contexts)
    
    # Chat
    try:
        response = await chat_with_agent(request.message, history, file_context)
    except Exception as e:
        response = f'Ошибка: {str(e)}. Проверьте API ключ и модель.'
    
    # Update history
    history.append({'role': 'user', 'content': request.message, 'ts': datetime.now().isoformat()})
    history.append({'role': 'assistant', 'content': response, 'ts': datetime.now().isoformat()})
    
    if len(history) > 50:
        chat_sessions[session_id] = history[-50:]
    
    return ChatResponse(
        response=response,
        session_id=session_id,
        suggestions=get_suggestions(request.message)
    )

@app.get('/session/{session_id}')
async def get_session(session_id: str):
    return {'messages': chat_sessions.get(session_id, [])}

@app.delete('/session/{session_id}')
async def clear_session(session_id: str):
    chat_sessions.pop(session_id, None)
    return {'status': 'cleared'}

# ============================================================================
# Run
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    print(f'''
╔════════════════════════════════════════════════════════╗
║         CZ Career Architect API v{VERSION}               ║
╠════════════════════════════════════════════════════════╣
║  🌐 Server:   http://localhost:8000                    ║
║  📚 API Docs: http://localhost:8000/docs               ║
║  💬 Chat:     http://localhost:8000                    ║
║  🤖 Model:    {os.getenv('OPENAI_MODEL', 'gpt-5.2'):40} ║
╚════════════════════════════════════════════════════════╝
    ''')
    uvicorn.run(app, host='0.0.0.0', port=8000)
