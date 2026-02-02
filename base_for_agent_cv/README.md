# CZ Career Architect

AI-ассистент для создания HR-документов для чешского здравоохранения.

**Version:** 2.0.0 | **Model:** gpt-5.2 | **Updated:** 2026-01-27

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements_api.txt -r requirements_dev.txt

# 2. Запустить сервер (каноничный entrypoint)
./run_api.sh

# 3. Открыть чат
open http://localhost:8000
```

> Примечание: `api.py` — legacy entrypoint. Основное приложение живёт в `app/main.py`.

## Что нового в v2.0.0

- Chat-first режим — естественный диалог без команд
- RAG-mandatory — обязательное использование базы знаний
- gpt-5.2 — новая модель
- Упрощённая структура — компактный системный промпт

## Возможности

- CV: ATS-safe, ČSN 01 6910
- Письма: Мотивационные, HR emails
- Проверка: GDPR/ATS валидация
- Чат: Естественный диалог
- Файлы: PDF, DOCX, TXT

## GDPR Правила

Запрещено: Дата рождения, Фото, Семейный статус, Гражданство, Rodné číslo
Разрешено: Имя, Город, Email, Телефон, Опыт, Nostrifikace status

## API Endpoints (canonical)

- GET / — Веб-чат (если есть `frontend/index.html`)
- GET /docs — Swagger UI
- GET /health — Статус
- POST /chat/ — Сообщение
- GET /chat/session/{session_id} — История
- DELETE /chat/session/{session_id} — Очистить историю
- POST /files/upload — Загрузить файл
- GET /files/ — Список файлов
- DELETE /files/{file_id} — Удалить файл

## Legacy aliases (compat)

Для совместимости также доступны старые пути (без Swagger):
- POST /chat
- POST /upload
- GET /files
- GET/DELETE /session/{session_id}

## Конфигурация (.env)

Скопируй `.env.example` → `.env` и заполни.

Минимум:
- `OPENAI_API_KEY`

Рекомендуется для деплоя (чтобы защитить ключ и бюджет):
- `API_KEY` (тогда все запросы требуют заголовок `X-API-Key`)

Пример:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
API_KEY=change-me
CORS_ALLOW_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
CORS_ALLOW_CREDENTIALS=false
```

(Опционально) `OPENAI_VECTOR_STORE_ID` — если/когда будет реально подключён.

---

CZ Career Architect v2.0.0 | Model: gpt-5.2
