from fastapi.testclient import TestClient


def test_chat_does_not_include_files_from_other_session(client: TestClient, monkeypatch):
    # Upload file under session s1
    upload = client.post(
        "/files/upload",
        files={"file": ("a.txt", b"SECRET", "text/plain"), "session_id": (None, "s1")},
    )
    assert upload.status_code == 200
    file_id = upload.json()["id"]

    from app.routers import chat as chat_router

    captured = {"file_context": None}

    async def stub_chat_with_agent(message, history=None, file_context=None):
        captured["file_context"] = file_context
        return "ok"

    monkeypatch.setattr(chat_router, "chat_with_agent", stub_chat_with_agent)

    # Request from a different session must not include file content
    resp = client.post(
        "/chat/",
        json={"message": "use file", "file_ids": [file_id], "session_id": "s2"},
    )
    assert resp.status_code == 200
    assert captured["file_context"] in (None, "")


def test_chat_rejects_file_ids_without_session_id(client: TestClient, monkeypatch):
    from app.routers import chat as chat_router

    async def stub_chat_with_agent(message, history=None, file_context=None):
        return "ok"

    monkeypatch.setattr(chat_router, "chat_with_agent", stub_chat_with_agent)

    resp = client.post("/chat/", json={"message": "hi", "file_ids": ["deadbeef"]})
    assert resp.status_code == 400
