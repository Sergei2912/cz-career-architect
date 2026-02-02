from fastapi.testclient import TestClient


def test_chat_uses_provided_session_id_and_appends_history(client: TestClient, monkeypatch):
    # Make deterministic: avoid calling OpenAI.
    from app.routers import chat as chat_router

    async def stub_chat_with_agent(message, history=None, file_context=None):
        return "ok"

    monkeypatch.setattr(chat_router, "chat_with_agent", stub_chat_with_agent)

    resp = client.post("/chat/", json={"message": "hi", "session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "s1"

    resp = client.post("/chat/", json={"message": "hi2", "session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "s1"

    resp = client.get("/chat/session/s1")
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    # Each chat adds user+assistant
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_chat_includes_uploaded_file_context_when_file_ids_given(client: TestClient, monkeypatch):
    # Upload a file
    upload = client.post(
        "/files/upload",
        files={"file": ("cv.txt", b"Hello from file", "text/plain")},
    )
    file_id = upload.json()["id"]

    from app.routers import chat as chat_router

    captured = {"file_context": None}

    async def stub_chat_with_agent(message, history=None, file_context=None):
        captured["file_context"] = file_context
        return "ok"

    monkeypatch.setattr(chat_router, "chat_with_agent", stub_chat_with_agent)

    resp = client.post(
        "/chat/",
        json={"message": "use file", "file_ids": [file_id], "session_id": "s1"},
    )
    assert resp.status_code == 200

    assert captured["file_context"]
    assert "Файл 'cv.txt'" in captured["file_context"]
    assert "Hello from file" in captured["file_context"]


def test_chat_history_is_trimmed_to_last_50_messages(client: TestClient, monkeypatch):
    from app.routers import chat as chat_router

    async def stub_chat_with_agent(message, history=None, file_context=None):
        return "ok"

    monkeypatch.setattr(chat_router, "chat_with_agent", stub_chat_with_agent)

    for i in range(30):
        resp = client.post("/chat/", json={"message": f"m{i}", "session_id": "s1"})
        assert resp.status_code == 200

    resp = client.get("/chat/session/s1")
    messages = resp.json()["messages"]
    assert len(messages) == 50


def test_chat_agent_failure_is_graceful(client: TestClient, monkeypatch):
    from app.routers import chat as chat_router

    async def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(chat_router, "chat_with_agent", boom)

    resp = client.post("/chat/", json={"message": "hi", "session_id": "s1"})
    assert resp.status_code == 200
    assert "Извини, произошла ошибка" in resp.json()["response"]
