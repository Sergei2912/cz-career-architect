from fastapi.testclient import TestClient


def test_files_are_scoped_by_session_id(client: TestClient):
    # Upload file for session s1
    r1 = client.post(
        "/files/upload",
        files={"file": ("a.txt", b"a", "text/plain"), "session_id": (None, "s1")},
    )
    assert r1.status_code == 200

    # Upload file for session s2
    r2 = client.post(
        "/files/upload",
        files={"file": ("b.txt", b"b", "text/plain"), "session_id": (None, "s2")},
    )
    assert r2.status_code == 200

    files_s1 = client.get("/files/", params={"session_id": "s1"}).json()
    files_s2 = client.get("/files/", params={"session_id": "s2"}).json()

    assert len(files_s1) == 1
    assert len(files_s2) == 1
    assert files_s1[0]["name"] == "a.txt"
    assert files_s2[0]["name"] == "b.txt"
