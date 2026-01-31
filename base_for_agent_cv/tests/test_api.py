from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_upload_file_invalid_extension(client: TestClient, tmp_path):
    # Create dummy file
    d = tmp_path / "test.exe"
    d.write_text("content")
    
    with open(d, "rb") as f:
        response = client.post("/files/upload", files={"file": ("test.exe", f, "application/octet-stream")})
    
    assert response.status_code == 400
    assert "не поддерживается" in response.text

def test_chat_session_lifecycle(client: TestClient):
    # 1. Start chat
    response = client.post("/chat/", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]
    assert session_id is not None
    
    # 2. Get history
    response = client.get(f"/chat/session/{session_id}")
    assert response.status_code == 200
    assert len(response.json()["messages"]) >= 2  # User + Assistant
    
    # 3. Clear history
    response = client.delete(f"/chat/session/{session_id}")
    assert response.status_code == 200
    
    # 4. Dictionary check (should be empty/gone)
    response = client.get(f"/chat/session/{session_id}")
    assert response.json()["messages"] == []
