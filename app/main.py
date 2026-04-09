from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.database import engine, Base
from app.models import Student
from app.routers import router
from app.auth import hash_password, verify_password, create_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student API",
    description="A simple REST API for managing student records",
    version="1.0.0"
)

app.include_router(router)

# Hardcoded user for now — in a real app this comes from a users table in DB
FAKE_USER = {
    "username": "admin",
    "password": hash_password("secret123")
}

@app.get("/")
def root():
    return {"message": "Welcome to the Student API"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != FAKE_USER["username"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(form_data.password, FAKE_USER["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}
