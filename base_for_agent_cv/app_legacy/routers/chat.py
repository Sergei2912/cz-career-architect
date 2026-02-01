import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter

from ..models.schemas import ChatRequest, ChatResponse
from ..services.agent_service import chat_with_agent, get_suggestions
from .files import get_uploaded_files_store

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory storage for chat sessions
chat_sessions: dict[str, list] = {}

uploaded_files = get_uploaded_files_store()

@router.post('/', response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get or create session history
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    history = chat_sessions[session_id]
    
    # Get file context
    file_context = None
    if request.file_ids:
        contexts = []
        for fid in request.file_ids:
            if fid in uploaded_files:
                f = uploaded_files[fid]
                contexts.append(f"Файл '{f['name']}':\n{f['text'][:2000]}")
        if contexts:
            file_context = '\n\n'.join(contexts)
    
    # Chat with agent
    try:
        response = await chat_with_agent(request.message, history, file_context)
    except Exception as e:
        response = f'Извини, произошла ошибка: {str(e)}. Попробуй ещё раз.'
    
    # Update history
    history.append({'role': 'user', 'content': request.message, 'ts': datetime.now().isoformat()})
    history.append({'role': 'assistant', 'content': response, 'ts': datetime.now().isoformat()})
    
    # Keep only last 50 messages
    if len(history) > 50:
        chat_sessions[session_id] = history[-50:]
    
    # Get suggestions
    suggestions = get_suggestions(request.message, response)
    
    return ChatResponse(
        response=response,
        session_id=session_id,
        suggestions=suggestions
    )

@router.get('/session/{session_id}')
async def get_session(session_id: str):
    if session_id not in chat_sessions:
        return {'messages': []}
    return {'messages': chat_sessions[session_id]}

@router.delete('/session/{session_id}')
async def clear_session(session_id: str):
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {'status': 'cleared'}
