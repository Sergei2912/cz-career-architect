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
- POST /files/upload — Загрузить файл (требует session_id / X-Session-Id)
- GET /files/ — Список файлов (требует session_id / X-Session-Id)
- DELETE /files/{file_id} — Удалить файл (требует session_id / X-Session-Id)

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

## Context7 MCP Server

Проект интегрирован с Context7 MCP (Model Context Protocol) сервером для расширенного управления контекстом.

### Что такое Context7 MCP?

Context7 MCP — это сервер Model Context Protocol от Upstash, который обеспечивает:
- Долговременное хранение контекста в Redis
- Управление сессиями для AI-ассистентов
- Кроссплатформенную совместимость через стандартный протокол

Подробнее: [Context7 MCP Documentation](https://github.com/upstash/context7-mcp)

### Быстрый старт с MCP

```bash
# 1. Установить Node.js зависимости (если еще не установлены)
npm install

# 2. Настроить переменные окружения для Upstash Redis
# Добавь в .env:
# UPSTASH_REDIS_REST_URL=your_url_here
# UPSTASH_REDIS_REST_TOKEN=your_token_here

# 3. Валидировать конфигурацию MCP
./validate-mcp-config.sh

# 4. Запустить интеграционный тест
npm run test:mcp
```

### Конфигурация (.mcp.json)

MCP сервер настраивается через `.mcp.json`:
- Версия зафиксирована на `@upstash/context7-mcp@2.1.1` для стабильности
- Требуются переменные окружения: `UPSTASH_REDIS_REST_URL` и `UPSTASH_REDIS_REST_TOKEN`

### Docker поддержка

Запустить MCP сервер в контейнере:

```bash
# Собрать образ
docker build -t cz-career-architect-mcp .

# Запустить с переменными окружения
docker run -e UPSTASH_REDIS_REST_URL=your_url \
           -e UPSTASH_REDIS_REST_TOKEN=your_token \
           cz-career-architect-mcp
```

### Разработка

- **Валидация**: `./validate-mcp-config.sh` проверяет корректность `.mcp.json`
- **Тестирование**: `npm run test:mcp` запускает интеграционные тесты
- **Логирование**: Все операции MCP логируются в `mcp.log` через winston

---

CZ Career Architect v2.0.0 | Model: gpt-5.2
