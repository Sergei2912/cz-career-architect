# CZ Career Architect - Architecture Documentation

## Overview

CZ Career Architect is a FastAPI-based AI assistant for medical professionals relocating to Czech Republic. It generates GDPR-compliant, ATS-compatible HR documents (CV, cover letters) using GPT-5.2 with mandatory RAG (Retrieval-Augmented Generation) integration.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                   (Frontend / API Client)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Server (api.py)                    │
│                        v2.0.0                                │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                  │
│  • GET  /              → Frontend                            │
│  • GET  /health        → Status + RAG + Storage              │
│  • POST /upload        → File upload with GDPR check         │
│  • GET  /files         → List uploaded files                 │
│  • POST /chat          → Chat with AI agent                  │
│  • GET  /session/{id}  → Get conversation history            │
└────┬──────────────┬─────────────────┬────────────────────────┘
     │              │                 │
     │              │                 │
┌────▼─────┐  ┌────▼────────┐  ┌────▼──────────┐
│  Agent   │  │  Database   │  │  Validators   │
│  System  │  │   Layer     │  │    (GDPR/     │
│ (agents. │  │(database.py)│  │   ČSN/ATS)    │
│   py)    │  │             │  │               │
└────┬─────┘  └────┬────────┘  └───────────────┘
     │              │
     │              │
┌────▼─────────────────────────────┐
│     OpenAI GPT-5.2 + RAG         │
│   (with Vector Store search)     │
└──────────────────────────────────┘
```

---

## Component Details

### 1. API Server (api.py v2.0.0)

**Primary Entry Point:** The unified FastAPI application.

**Key Features:**
- Chat-first interaction model
- RAG integration with OpenAI vector stores
- GDPR/ATS/ČSN validation on upload
- Persistent storage (SQLite or in-memory)
- Session management with auto-cleanup

**Configuration:**
- Model: `gpt-5.2` (configurable via env)
- System Prompt: English with multilingual support
- Max file size: 10 MB
- Allowed formats: PDF, DOCX, DOC, TXT, RTF

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...                   # Required
OPENAI_MODEL=gpt-5.2                    # Optional (default)
OPENAI_VECTOR_STORE_ID=vs_...           # For RAG
SESSION_EXPIRY_DAYS=7                   # Session cleanup
FILE_EXPIRY_DAYS=7                      # File cleanup
```

---

### 2. Agent System (agents.py + config.py)

**Purpose:** Wrapper around OpenAI API with RAG integration.

**Key Components:**

#### Agent Class
- Name, instructions (system prompt), model
- Tools (FileSearchTool for RAG)
- Output schema (for structured responses)
- ModelSettings (temperature, response_include)

#### FileSearchTool
```python
FileSearchTool(
    vector_store_ids=["vs_..."],
    max_num_results=5,
    include_search_results=True
)
```

#### Runner
- Executes agent with conversation history
- Returns structured or text output
- Handles errors gracefully

**RAG Integration:**
- Mandatory per system prompt requirements
- Searches knowledge base for compliance info
- Returns relevant citations
- Configurable max results (default: 5)

---

### 3. Database Layer (database.py)

**Purpose:** Persistent storage for sessions and files.

**Technology:** SQLAlchemy + SQLite

**Tables:**

#### chat_sessions
```sql
CREATE TABLE chat_sessions (
    id VARCHAR PRIMARY KEY,
    created_at DATETIME,
    updated_at DATETIME,
    messages_json TEXT,      -- JSON array
    active BOOLEAN
);
```

#### uploaded_files
```sql
CREATE TABLE uploaded_files (
    id VARCHAR PRIMARY KEY,
    filename VARCHAR,
    size INTEGER,
    file_type VARCHAR,
    file_path VARCHAR,
    uploaded_at DATETIME,
    text_content TEXT,
    preview TEXT,
    issues_json TEXT,        -- JSON array
    active BOOLEAN
);
```

**Features:**
- Automatic cleanup of old sessions/files
- Soft deletes (preserve audit trail)
- Graceful fallback to in-memory if unavailable
- ACID transactions

**Location:** `base_for_agent_cv/data/cz_career_architect.db`

---

### 4. Validators (packages/validators/)

**Purpose:** Compliance checking for documents.

**Modules:**

#### cz_cv_validator_adapter.py
- GDPR checks (birth date, photo, marital status, etc.)
- ČSN 01 6910 typography (dates, phone, numbers)
- ATS compatibility (no tables, columns, graphics)
- JSON schema validation

**GDPR Rules (Blocked):**
- ❌ Birth date, age, rodné číslo
- ❌ Photo, marital status, children
- ❌ Nationality, ethnicity, religion
- ❌ Full address (only city + country)
- ❌ Reference contact details

**ČSN Typography:**
- ✅ Dates: `15. 1. 2025` (spaces after dots)
- ✅ Phone: `+420 777 123 456`
- ✅ Numbers: `25 000 Kč` (space separator)
- ✅ En-dash in ranges: `2020–2023`

**ATS Rules:**
- ✅ No tables, columns, graphics
- ✅ Linear structure
- ✅ Single language (cs-CZ default)
- ✅ 1-2 pages max

---

### 5. Configuration (config.py)

**Purpose:** Centralized configuration management.

**Key Functions:**
```python
resolve_model()              # → "gpt-5.2"
resolve_vector_store_ids()   # → ["vs_..."]
resolve_assistant_id()       # → "asst_..."
resolve_model_settings()     # → ModelSettings(...)
```

**Constants:**
```python
VERSION = "2.0.0"
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_VECTOR_STORE_ID = "vs_..."
```

---

## Data Flow

### Chat Request Flow

```
1. User sends message
   POST /chat { "message": "...", "session_id": "..." }
   
2. API loads session history from database
   db_manager.get_chat_history(session_id)
   
3. If file_ids provided, load file content
   db_manager.get_uploaded_file(file_id)
   
4. Build context (history + files + message)
   
5. Call agent with RAG enabled
   Agent → OpenAI GPT-5.2 + Vector Store Search
   
6. Receive response with RAG citations
   
7. Append to history and save to database
   db_manager.update_chat_history(session_id, messages)
   
8. Return response to user
   { "response": "...", "session_id": "...", "suggestions": [...] }
```

### File Upload Flow

```
1. User uploads file
   POST /upload (multipart/form-data)
   
2. Validate extension and size
   
3. Save to disk (uploads/ directory)
   
4. Extract text content
   • PDF: PyMuPDF or pdfplumber
   • DOCX: python-docx
   • TXT: direct read
   
5. Run GDPR/ČSN/ATS validation
   check_gdpr(text) + check_csn_typography(text)
   
6. Save metadata to database
   db_manager.save_uploaded_file(...)
   
7. Return file info with issues
   { "id": "...", "name": "...", "issues": [...] }
```

---

## Deployment

### Production Setup

```bash
# 1. Clone repository
git clone https://github.com/Sergei2912/cz-career-architect.git
cd cz-career-architect

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your keys

# 4. Run server
cd base_for_agent_cv
python api.py
```

### Environment Requirements

**Required:**
- Python 3.9+
- OpenAI API key with GPT-5.2 access
- Vector store ID (for RAG)

**Optional:**
- SQLAlchemy (for persistence)
- Redis (for caching - future)
- Celery (for async jobs - future)

### Server Output

```
✅ Using SQLite database for persistence
   Cleaned up 0 old sessions, 0 old files

╔════════════════════════════════════════════════════════╗
║         CZ Career Architect API v2.0.0                 ║
╠════════════════════════════════════════════════════════╣
║  🌐 Server:   http://localhost:8000                    ║
║  📚 API Docs: http://localhost:8000/docs               ║
║  💬 Chat:     http://localhost:8000                    ║
║  🤖 Model:    gpt-5.2                                  ║
╚════════════════════════════════════════════════════════╝
```

---

## API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "online",
  "version": "2.0.0",
  "model": "gpt-5.2",
  "rag_enabled": true,
  "vector_stores": 1,
  "storage": "sqlite"
}
```

### Upload File
```http
POST /upload
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "id": "a1b2c3d4_5678",
  "name": "cv.pdf",
  "size": 123456,
  "type": "pdf",
  "uploaded_at": "2026-02-01T12:00:00",
  "preview": "John Doe\nDentist...",
  "issues": [
    "❌ Дата рождения/возраст — удалить",
    "⚠️ Телефон: +420 xxx xxx xxx"
  ]
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Create a CV for a dentist",
  "session_id": "optional-uuid",
  "file_ids": ["file-id-1", "file-id-2"]
}
```

**Response:**
```json
{
  "response": "I'll help you create a CV...",
  "session_id": "uuid-1234",
  "suggestions": [
    "Add cover letter",
    "Check GDPR compliance",
    "Export to DOCX"
  ]
}
```

### List Files
```http
GET /files
```

### Delete File
```http
DELETE /files/{file_id}
```

### Get Session
```http
GET /session/{session_id}
```

### Clear Session
```http
DELETE /session/{session_id}
```

---

## Legacy Code

The previous implementation (`app/main.py` v1.2.3) has been moved to `app_legacy/` directory.

**Key Differences:**

| Feature | Legacy (v1.2.3) | Current (v2.0.0) |
|---------|----------------|------------------|
| Entry Point | app/main.py | api.py |
| Model | gpt-4o-mini | gpt-5.2 |
| Prompt | Russian | English (multilingual) |
| RAG | Not integrated | Fully integrated ✅ |
| Storage | In-memory only | SQLite + fallback |
| Architecture | Modular (routers/services) | Unified monolithic |

**Migration:** See `app_legacy/README.md` for details.

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=base_for_agent_cv --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

**Test Files:**
- `test_api.py` - API endpoints
- `test_config.py` - Configuration
- `test_validator.py` - GDPR/ČSN validation
- `test_exceptions.py` - Error handling

---

## Security Considerations

1. **GDPR Compliance:** Automatic validation blocks prohibited fields
2. **Input Validation:** Pydantic models validate all inputs
3. **SQL Injection:** Protected by SQLAlchemy ORM
4. **XSS Prevention:** Text sanitization in validators
5. **File Upload:** Size limits and extension validation
6. **API Keys:** Never logged or exposed
7. **Session Isolation:** Each session independent

---

## Performance

**Optimizations:**
- Database indexed queries
- Session history limited to last 50 messages
- File text extraction cached
- Automatic cleanup of old data

**Benchmarks:**
- Chat response: 2-5 seconds (depends on GPT-5.2)
- File upload: <1 second
- Database queries: <10ms

---

## Monitoring

**Health endpoint** provides system status:
- API online status
- Model version
- RAG enabled status
- Storage type (sqlite/in-memory)

**Future additions:**
- Prometheus metrics
- Request duration tracking
- Error rate monitoring
- Cache hit rates

---

## Future Enhancements

See `IMPROVEMENTS_RU.md` for detailed roadmap:

1. **Caching Layer** (Redis for GPT responses)
2. **Async Processing** (Celery for long-running jobs)
3. **i18n Support** (Multi-language UI)
4. **API Versioning** (/api/v1, /api/v2)
5. **Mobile App** (React Native/Flutter)
6. **Job Board Integration** (Auto-apply feature)
7. **Interview Prep** (AI interview coach)

---

## Support

- **Issues:** https://github.com/Sergei2912/cz-career-architect/issues
- **Documentation:** See README.md, AGENTS.md
- **API Docs:** http://localhost:8000/docs (when running)

---

**Version:** 2.0.0  
**Last Updated:** 2026-02-01  
**Status:** Production Ready ✅
