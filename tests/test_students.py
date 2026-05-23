def test_create_student_success(client, auth_token):
    response = client.post(
        "/students/",
        json={
            "name": "sritama Hazra",
            "email": "sri1234@gmail.com",
            "age": 21,
            "gpa": 8.0,
            "course": "AIML"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "sritama Hazra"
    assert data["email"] == "sri1234@gmail.com"
    assert data["age"] == 21
    assert data["gpa"] == 8.0
    assert data["course"] == "AIML"
    assert "id" in data


def test_create_student_duplicate_email(client, auth_token, sample_student):
    response = client.post(
        "/students/",
        json={
            "name": "Another Student",
            "email": "sri1234@gmail.com",  # same email as sample_student
            "age": 21,
            "gpa": 7.0,
            "course": "Physics"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_create_student_invalid_name(client, auth_token):
    response = client.post(
        "/students/",
        json={
            "name": "A",           # too short
            "email": "test@mail.com",
            "age": 20,
            "gpa": 8.0,
            "course": "Math"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422


def test_create_student_invalid_age(client, auth_token):
    response = client.post(
        "/students/",
        json={
            "name": "Test Student",
            "email": "test@mail.com",
            "age": 150,            # age too high
            "gpa": 8.0,
            "course": "Math"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422


def test_create_student_invalid_gpa(client, auth_token):
    response = client.post(
        "/students/",
        json={
            "name": "Test Student",
            "email": "test@mail.com",
            "age": 20,
            "gpa": 11.0,           # gpa too high
            "course": "Math"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422


def test_create_student_invalid_email(client, auth_token):
    response = client.post(
        "/students/",
        json={
            "name": "Test Student",
            "email": "notanemail",  # invalid email
            "age": 20,
            "gpa": 8.0,
            "course": "Math"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422




def test_get_all_students(client, sample_student):
    response = client.get("/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_get_all_students_empty(client):
    response = client.get("/students/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_student_by_id(client, sample_student):
    student_id = sample_student["id"]
    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["id"] == student_id
    assert response.json()["name"] == "sritama Hazra"


def test_get_student_not_found(client):
    response = client.get("/students/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"



def test_update_student_success(client, auth_token, sample_student):
    student_id = sample_student["id"]
    response = client.put(
        f"/students/{student_id}",
        json={"gpa": 9.5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["gpa"] == 9.5
    # Other fields should remain unchanged
    assert response.json()["name"] == "sritama Hazra"


def test_update_student_not_found(client, auth_token):
    response = client.put(
        "/students/99999",
        json={"gpa": 9.5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_update_student_invalid_gpa(client, auth_token, sample_student):
    student_id = sample_student["id"]
    response = client.put(
        f"/students/{student_id}",
        json={"gpa": 15.0},        # invalid gpa
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422



def test_delete_student_success(client, auth_token, sample_student):
    student_id = sample_student["id"]
    response = client.delete(
        f"/students/{student_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

  
    get_response = client.get(f"/students/{student_id}")
    assert get_response.status_code == 404


def test_delete_student_not_found(client, auth_token):
    response = client.delete(
        "/students/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404




def test_pagination_page_size(client, auth_token):
    # Create 5 students
    student_names = ["Student A", "Student B", "Student C", "Student D", "Student E"]
    for i, name in enumerate(student_names):
        client.post(
            "/students/",
            json={
                "name": name,
                "email": f"student{i}@mail.com",
                "age": 20 + i,
                "gpa": 7.0 + i * 0.5,
                "course": "Computer Science"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

   
    response = client.get("/students/?page=1&size=3")
    assert response.status_code == 200
    assert len(response.json()) == 3

   
    response = client.get("/students/?page=2&size=3")
    assert response.status_code == 200
    assert len(response.json()) == 2




def test_filter_by_course(client, auth_token):
    
    client.post("/students/", json={
        "name": "CS Student",
        "email": "cs@mail.com",
        "age": 20, "gpa": 8.0,
        "course": "Computer Science"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    client.post("/students/", json={
        "name": "Math Student",
        "email": "math@mail.com",
        "age": 21, "gpa": 7.5,
        "course": "Mathematics"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/students/?course=Computer Science")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["course"] == "Computer Science"


def test_filter_by_gpa_range(client, auth_token):
    client.post("/students/", json={
        "name": "High GPA",
        "email": "high@mail.com",
        "age": 20, "gpa": 9.5,
        "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    client.post("/students/", json={
        "name": "Low GPA",
        "email": "low@mail.com",
        "age": 20, "gpa": 5.0,
        "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/students/?min_gpa=8.0&max_gpa=10.0")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["gpa"] == 9.5


def test_search_by_name(client, auth_token):
    client.post("/students/", json={
        "name": "Sritama Hazra",
        "email": "sri1234@gmail.com",
        "age": 21, "gpa": 8.0,
        "course": "AIML"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    client.post("/students/", json={
        "name": "Priya Das",
        "email": "priya@mail.com",
        "age": 21, "gpa": 7.5,
        "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/students/?search=Sritama")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Sritama Hazra"




def test_sort_by_gpa_desc(client, auth_token):
    client.post("/students/", json={
        "name": "Student A", "email": "a@mail.com",
        "age": 20, "gpa": 6.0, "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    client.post("/students/", json={
        "name": "Student B", "email": "b@mail.com",
        "age": 21, "gpa": 9.0, "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    client.post("/students/", json={
        "name": "Student C", "email": "c@mail.com",
        "age": 22, "gpa": 7.5, "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/students/?sort_by=gpa&order=desc")
    assert response.status_code == 200
    gpas = [s["gpa"] for s in response.json()]
    assert gpas == sorted(gpas, reverse=True)


def test_sort_by_name_asc(client, auth_token):
    client.post("/students/", json={
        "name": "Zara Khan", "email": "zara@mail.com",
        "age": 20, "gpa": 8.0, "course": "CS"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    client.post("/students/", json={
        "name": "Sritama Hazra", "email": "sri1234@gmail.com",
        "age": 21, "gpa": 8.0, "course": "AIML"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/students/?sort_by=name&order=asc")
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert names == sorted(names)


def test_invalid_sort_field(client):
    response = client.get("/students/?sort_by=invalid_field")
    assert response.status_code == 400