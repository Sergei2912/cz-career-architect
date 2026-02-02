from fastapi.testclient import TestClient


def test_upload_file_txt_success_returns_fileinfo_and_issues(client: TestClient):
    content = "Datum narození: 15.1.1985\nPraxe 2015-2023\n"
    resp = client.post(
        "/files/upload",
        files={
            "file": ("cv.txt", content.encode("utf-8"), "text/plain"),
            "session_id": (None, "s1"),
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "id" in data and data["id"]
    assert data["name"] == "cv.txt"
    assert data["type"] == "txt"
    assert data["size"] == len(content.encode("utf-8"))
    assert "uploaded_at" in data

    # preview should include content or its prefix
    assert "preview" in data
    assert "Datum narození" in (data["preview"] or "")

    # issues should be a list (can be empty depending on rules)
    assert "issues" in data
    assert isinstance(data["issues"], list)


def test_upload_file_too_large_returns_400(client: TestClient):
    # MAX_FILE_SIZE is 10MB; create a payload slightly larger.
    big = b"a" * (10 * 1024 * 1024 + 1)
    resp = client.post(
        "/files/upload",
        files={"file": ("big.txt", big, "text/plain"), "session_id": (None, "s1")},
    )
    assert resp.status_code == 400
    assert "Файл слишком большой" in resp.text


def test_list_files_returns_uploaded_files_without_text_or_path(client: TestClient):
    resp = client.post(
        "/files/upload",
        files={"file": ("cv.txt", b"hello", "text/plain"), "session_id": (None, "s1")},
    )
    assert resp.status_code == 200

    # Without session id, list is empty (privacy)
    resp = client.get("/files/")
    assert resp.status_code == 200
    assert resp.json() == []

    resp = client.get("/files/", params={"session_id": "s1"})
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) == 1

    item = items[0]
    assert "id" in item
    assert "name" in item
    assert "size" in item
    assert "type" in item
    assert "uploaded_at" in item

    # Ensure we never leak internal fields
    assert "text" not in item
    assert "path" not in item


def test_delete_file_removes_from_store_and_list(client: TestClient):
    resp = client.post(
        "/files/upload",
        files={"file": ("cv.txt", b"hello", "text/plain"), "session_id": (None, "s1")},
    )
    file_id = resp.json()["id"]

    # Without session id, list is empty (privacy)
    resp = client.get("/files/")
    assert resp.status_code == 200
    assert resp.json() == []

    # With session id, it appears
    resp = client.get("/files/", params={"session_id": "s1"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Delete with correct session id
    resp = client.delete(f"/files/{file_id}", params={"session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    resp = client.get("/files/", params={"session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_file_missing_returns_404(client: TestClient):
    resp = client.delete("/files/not_exist")
    assert resp.status_code == 404
    assert "Файл не найден" in resp.text
