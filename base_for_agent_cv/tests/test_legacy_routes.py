from fastapi.testclient import TestClient


def test_legacy_upload_requires_and_accepts_session_id(client: TestClient):
    # Missing session should fail (privacy rule enforced by canonical upload handler)
    r = client.post(
        "/upload",
        files={"file": ("a.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400

    # With session_id form field should work
    r = client.post(
        "/upload",
        files={"file": ("a.txt", b"hello", "text/plain"), "session_id": (None, "s1")},
    )
    assert r.status_code == 200


def test_legacy_list_files_forwards_session_id(client: TestClient):
    # Upload under s1
    r = client.post(
        "/upload",
        files={"file": ("a.txt", b"hello", "text/plain"), "session_id": (None, "s1")},
    )
    assert r.status_code == 200

    # Legacy list without session id returns empty
    r = client.get("/files")
    assert r.status_code == 200
    assert r.json() == []

    # Legacy list with session id returns the file
    r = client.get("/files", params={"session_id": "s1"})
    assert r.status_code == 200
    assert len(r.json()) == 1
