# Legacy Application (v1.2.3)

⚠️ **DEPRECATED** - This version is no longer actively maintained.

## Migration Notice

This directory contains the legacy modular implementation (v1.2.3) which has been superseded by the unified `api.py` (v2.0.0).

### Key Differences

| Feature | Legacy (v1.2.3) | Current (v2.0.0) |
|---------|----------------|------------------|
| **Entry Point** | `app/main.py` | `api.py` |
| **Model** | gpt-4o-mini | gpt-5.2 |
| **System Prompt** | Russian | English (multilingual support) |
| **RAG Integration** | Not integrated | Fully integrated with file_search |
| **Architecture** | Modular (routers/services) | Unified monolithic |
| **Version** | 1.2.3 | 2.0.0 |

### Migration Guide

If you were using the legacy app, switch to the new api.py:

**Old:**
```bash
cd base_for_agent_cv
python app/main.py
```

**New:**
```bash
cd base_for_agent_cv
python api.py
```

### Why Was It Deprecated?

1. **Dual implementations** caused confusion and maintenance overhead
2. **RAG not integrated** - mandatory requirement per system prompt
3. **Inconsistent model defaults** - different from documented v2.0.0
4. **Different prompts** - Russian vs English caused issues

### If You Need Legacy Functionality

The legacy code remains available in this directory for reference. Key modules:

- `app/main.py` - Legacy FastAPI entry point
- `app/routers/` - Route handlers
- `app/services/agent_service.py` - Agent with Russian prompt

**Note:** Tests and documentation now reference the v2.0.0 api.py only.

### Support

For questions about migration, see the main README.md or open an issue.

---

**Archived:** 2026-02-01  
**Last Version:** 1.2.3  
**Replaced By:** api.py v2.0.0
