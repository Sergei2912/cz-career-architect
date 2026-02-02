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

## API Endpoints

- GET / — Веб-чат
- GET /health — Статус
- POST /chat — Сообщение
- POST /upload — Файл
- GET /files — Список

## Конфигурация (.env)

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
OPENAI_VECTOR_STORE_ID=vs_697776db24488191bf2f9bf0528d2845

---

CZ Career Architect v2.0.0 | Model: gpt-5.2
