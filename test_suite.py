import pytest
from app import app, init_db, DATABASE
import sqlite3
import os

@pytest.fixture
def client():
    # Setup test client and database
    app.config['TESTING'] = True
    with app.test_client() as client:
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
        init_db()  # Reinitialize the database
        yield client

def test_register_user(client):
    payload = {"username": "testuser", "email": "test@example.com"}
    response = client.post('/register', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "password" in data

    # Test duplicate registration
    response = client.post('/register', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_authenticate_user(client):
    # Register a user
    payload = {"username": "authuser", "email": "auth@example.com"}
    response = client.post('/register', json=payload)
    assert response.status_code == 201
    password = response.get_json()["password"]

    # Authenticate with correct credentials
    auth_payload = {"username": "authuser", "password": password}
    response = client.post('/auth', json=auth_payload)
    assert response.status_code == 200

    # Authenticate with incorrect credentials
    auth_payload["password"] = "wrongpassword"
    response = client.post('/auth', json=auth_payload)
    assert response.status_code == 401

def test_logs(client):
    # Verify logs are empty initially
    response = client.get('/logs')
    assert response.status_code == 200
    logs = response.get_json()
    assert logs == []

    # Register and authenticate a user to generate logs
    payload = {"username": "loguser", "email": "log@example.com"}
    response = client.post('/register', json=payload)
    assert response.status_code == 201
    password = response.get_json()["password"]

    auth_payload = {"username": "loguser", "password": password}
    client.post('/auth', json=auth_payload)

    # Verify logs
    response = client.get('/logs')
    logs = response.get_json()
    assert len(logs) == 1
