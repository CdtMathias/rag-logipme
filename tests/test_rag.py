from io import BytesIO

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_token():
    response = client.post("/login", data = {
        "username": "Mathias",
        "password": "test123"
    })
    return response.json()["access_token"]

def create_text_file(size_in_bytes: int, filename: str = "test.txt"):
    file_buffer = BytesIO()
    file_buffer.write(b"0" * size_in_bytes)
    file_buffer.name = filename
    file_buffer.seek(0)
    return file_buffer

def test_index_doc():
    token = get_token()
    file = create_text_file(1024 * 1)
    response = client.post("/index", headers = {
        "Authorization": f"Bearer {token}"
    },
    files = {
        "file": file
    }
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"{file.name} indexé avec succès."