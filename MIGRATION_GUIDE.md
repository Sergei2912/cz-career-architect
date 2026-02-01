# Migration Guide: v1.2.3 → v2.0.0

## Overview

This guide helps users migrate from the legacy implementation (v1.2.3, `app/main.py`) to the new unified API (v2.0.0, `api.py`).

---

## What Changed?

### High-Level Summary

| Aspect | v1.2.3 (Legacy) | v2.0.0 (Current) |
|--------|-----------------|------------------|
| **Entry Point** | `python app/main.py` | `python api.py` |
| **Model** | gpt-4o-mini | gpt-5.2 |
| **System Prompt** | Russian | English (multilingual) |
| **RAG** | Not integrated | Fully integrated ✅ |
| **Storage** | In-memory only | SQLite + in-memory fallback |
| **Architecture** | Modular (routers/services) | Unified monolithic |
| **Location** | `base_for_agent_cv/app/` | `base_for_agent_cv/api.py` |

---

## Why Migrate?

### Issues with Legacy (v1.2.3)

1. **No RAG Integration:** System prompt declares RAG mandatory, but it wasn't connected
2. **Wrong Model:** Used `gpt-4o-mini` instead of documented `gpt-5.2`
3. **Russian-Only Prompt:** Limited multilingual support
4. **In-Memory Only:** Lost all data on restart
5. **Dual Implementations:** Caused confusion and maintenance overhead

### Benefits of v2.0.0

1. ✅ **RAG Fully Integrated:** Vector store search working
2. ✅ **Correct Model:** Uses gpt-5.2 as documented
3. ✅ **Multilingual:** System prompt in English, responds in user's language
4. ✅ **Persistent Storage:** SQLite database survives restarts
5. ✅ **Single Source of Truth:** One implementation, clear documentation

---

## Migration Steps

### Step 1: Backup Current Data (if needed)

If you have important conversations or files:

```bash
# Legacy had no persistence, so nothing to backup
# If you modified the code, save your changes
```

### Step 2: Update Environment Variables

Check your `.env` file. You may need to add:

```bash
# Required (same as before)
OPENAI_API_KEY=sk-...

# Recommended (new)
OPENAI_MODEL=gpt-5.2                    # Explicitly set model
OPENAI_VECTOR_STORE_ID=vs_...           # For RAG
SESSION_EXPIRY_DAYS=7                    # Session cleanup
FILE_EXPIRY_DAYS=7                       # File cleanup
```

### Step 3: Install New Dependencies

```bash
# SQLAlchemy for persistence
pip install sqlalchemy>=2.0.0

# Or install all requirements
pip install -r requirements.txt
```

### Step 4: Change Startup Command

**Before (v1.2.3):**
```bash
cd base_for_agent_cv
python app/main.py
```

**After (v2.0.0):**
```bash
cd base_for_agent_cv
python api.py
```

### Step 5: Verify Server Started

Look for this output:

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

### Step 6: Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
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

---

## API Changes

### Endpoints (No Breaking Changes)

All endpoints remain the same:

✅ `GET  /` - Frontend  
✅ `GET  /health` - Status (enhanced with RAG info)  
✅ `POST /upload` - File upload  
✅ `GET  /files` - List files  
✅ `DELETE /files/{id}` - Delete file  
✅ `POST /chat` - Chat  
✅ `GET  /session/{id}` - Get session  
✅ `DELETE /session/{id}` - Clear session  

**No code changes needed in clients!**

### Response Format Changes

#### Health Endpoint

**Before:**
```json
{
  "status": "online",
  "version": "1.2.3",
  "model": "gpt-4o-mini"
}
```

**After:**
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

**Impact:** Clients checking `version` field need to handle "2.0.0"

---

## Behavioral Changes

### 1. System Prompt Language

**Before:** Russian-language prompt
```
"Ты — CZ Career Architect, дружелюбный AI-помощник..."
```

**After:** English prompt with multilingual support
```
"You are 'CZ Career Architect' — an AI assistant..."
```

**Impact:** 
- Agent still responds in user's language (Russian/English/Czech)
- Documents still generated in Czech
- No user-visible changes

### 2. RAG Integration

**Before:** No RAG, agent used only system prompt

**After:** Agent searches vector store for compliance info

**Impact:**
- More accurate responses about GDPR/ČSN rules
- Answers include citations from knowledge base
- May see `[Source: ...]` references in responses

### 3. Data Persistence

**Before:** All data in memory (lost on restart)

**After:** Saved to SQLite database

**Impact:**
- Sessions survive server restarts ✅
- Files metadata persists ✅
- Automatic cleanup after 7 days
- Database file: `base_for_agent_cv/data/cz_career_architect.db`

### 4. Model

**Before:** gpt-4o-mini

**After:** gpt-5.2 (more capable, same cost tier)

**Impact:**
- Better quality responses
- More accurate GDPR understanding
- Same API interface

---

## Code Migration (If You Customized)

### If You Modified `app/services/agent_service.py`

**Option 1:** Apply changes to `api.py`
- Edit `SYSTEM_PROMPT` in `api.py` (lines 50-118)
- Modify `create_agent()` function (lines 229-247)

**Option 2:** Create custom agent
```python
from agents import Agent, ModelSettings, FileSearchTool
from config import resolve_vector_store_ids

def create_custom_agent():
    return Agent(
        name='My Custom Agent',
        instructions='...',  # Your custom prompt
        model='gpt-5.2',
        model_settings=ModelSettings(),
        tools=[FileSearchTool(
            vector_store_ids=resolve_vector_store_ids(),
            max_num_results=5
        )]
    )
```

### If You Modified Routes

**Before:** `app/routers/chat.py`

**After:** Edit `api.py` endpoints directly
- Chat endpoint: line 350
- Upload endpoint: line 301
- Session endpoints: lines 389-396

---

## Testing Migration

### 1. Run Tests

```bash
pytest tests/ -v
```

All tests should pass (they've been updated for v2.0.0).

### 2. Manual Testing

```bash
# 1. Upload a file
curl -X POST http://localhost:8000/upload \
  -F "file=@test.pdf"

# 2. Start a chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!"}'

# 3. Check health
curl http://localhost:8000/health
```

### 3. Verify RAG

Ask a compliance question:

```json
POST /chat
{
  "message": "Can I include birth date in CV?"
}
```

Look for RAG citations in response (if configured).

---

## Rollback Plan (If Needed)

If you need to temporarily revert to legacy:

```bash
# 1. Go to legacy directory
cd base_for_agent_cv/app_legacy

# 2. Run legacy server
python main.py
```

**Note:** Legacy code is frozen at v1.2.3 and won't receive updates.

---

## Troubleshooting

### Problem: "Module 'app' not found"

**Cause:** Still trying to run legacy entry point

**Solution:** Use `python api.py` not `python app/main.py`

---

### Problem: "SQLAlchemy not available"

**Cause:** Missing dependency

**Solution:**
```bash
pip install sqlalchemy>=2.0.0
```

Or run in-memory mode (automatic fallback).

---

### Problem: "Vector store not found"

**Cause:** Missing `OPENAI_VECTOR_STORE_ID` in .env

**Solution:** Add to `.env`:
```bash
OPENAI_VECTOR_STORE_ID=vs_your_id_here
```

Or RAG will be disabled (agent still works).

---

### Problem: Different responses than before

**Cause:** Different model (gpt-5.2 vs gpt-4o-mini) and RAG

**Solution:** This is expected. New responses should be higher quality.

If you need gpt-4o-mini:
```bash
# In .env
OPENAI_MODEL=gpt-4o-mini
```

---

### Problem: Session data lost

**Cause:** Using in-memory fallback (no SQLAlchemy)

**Solution:** Install SQLAlchemy:
```bash
pip install sqlalchemy>=2.0.0
```

---

## Support

### Getting Help

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
2. See [README.md](README.md) for usage guide
3. Review [IMPROVEMENTS_RU.md](IMPROVEMENTS_RU.md) for roadmap
4. Open issue on GitHub if stuck

### Reporting Migration Issues

Include:
1. Previous version (1.2.3)
2. Current version (2.0.0)
3. Error message or unexpected behavior
4. Environment (Python version, OS)
5. `.env` configuration (without sensitive data)

---

## Post-Migration Checklist

After migration, verify:

- [ ] Server starts without errors
- [ ] Health endpoint shows v2.0.0
- [ ] RAG enabled (if configured)
- [ ] Storage shows "sqlite" (or "in-memory" if that's intended)
- [ ] Can upload files
- [ ] Can chat with agent
- [ ] Sessions persist after restart (if using SQLite)
- [ ] Old data no longer needed (legacy had no persistence)
- [ ] Tests pass
- [ ] Frontend/clients work (no API changes)

---

## Timeline

- **v1.2.3:** Legacy implementation (deprecated)
- **v2.0.0:** Current stable version (production ready)
- **Future:** See IMPROVEMENTS_RU.md for roadmap

---

## Conclusion

Migration from v1.2.3 to v2.0.0 is straightforward:

1. Change startup command: `python api.py`
2. Install SQLAlchemy (optional but recommended)
3. Configure RAG (optional but recommended)
4. Test and verify

**All API endpoints remain compatible** - no client code changes needed!

The new version provides:
- ✅ Better RAG integration
- ✅ Correct model (gpt-5.2)
- ✅ Persistent storage
- ✅ Single codebase
- ✅ Production ready

---

**Questions?** See [ARCHITECTURE.md](ARCHITECTURE.md) or open an issue.

**Last Updated:** 2026-02-01  
**Version:** 2.0.0
