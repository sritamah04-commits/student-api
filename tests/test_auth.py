def test_login_success(client):
    response = client.post(
        "/login",
        data = {"username": "admin", "password": "secret123" }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    response = client.post(
        "/login",
        data = {"username": "admin", "password": "wrongpassword" }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_wrong_username(client):
    response = client.post(
        "/login",
        data = {"username": "wronguser" , "password": "secret123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_protected_endppoint_without_token(client):
    response = client.post(
        "/students/",
        json = {
            "name": "Test Student",
            "email": "test@mail.com",
            "age": 20,
            "gpa": 8.0,
            "course": "Math"
        
        }

    )
    assert response.status_code == 401

def test_protected_endpoint_with_wrong_token(client):
    response = client.post(
        "/students/",
        json = {
            "name": "Test Student",
            "email": "test@mail.com",
            "age": 20,
            "gpa": 8.0,
            "course": "Math"
        },
        headers = {"Authorization": "Bearer wrong_token"}
    )
    assert response.status_code == 401
