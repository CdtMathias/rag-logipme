from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_success():
    response = client.post("/register", json ={
        "username": "testuserdw21",
        "password": "testpass" 
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Account created"

def test_register_duplicate():
    response = client.post("/register", json = {
        "username": "Mathias",
        "password": "test123"
    })
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"

def test_login_success():
    response = client.post("/login", data = {
        "username": "Mathias",
        "password": "test123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post("/login", data = {
        "username": "test123",
        "password": "passwordwedw"
    })
    assert response.status_code == 401
