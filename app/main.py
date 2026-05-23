from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse 
from fastapi.middleware.cors import CORSMiddleware
import time
from app.database import engine, Base
from app.models import Student
from app.routers import router
from app.auth import hash_password, verify_password, create_access_token
from app.logger import logger

Base.metadata.create_all(bind = engine)

app = FastAPI(
    title =  "student_api",
    description = " A REST API for managing student recrds",
    version = "2.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request - {request.method} {request.url}")
    response = await call_next(request)
    duration = round(time.time() - start_time, 4)
    logger.info(f"completed - {request.method} {request.url} | status_code={response.status_code} | duration = {duration}s")
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = "->".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}:{message}")
    logger.warning(f"Validation error on {request.method} {request.url}: {errors}")
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )





@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

app.include_router(router)

FAKE_USER = {
    "username": "admin",
    "password": hash_password("secret123")
}

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Student API"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for username='{form_data.username}'")
    if form_data.username != FAKE_USER["username"]:
        logger.warning(f"Failed login — invalid username='{form_data.username}'")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(form_data.password, FAKE_USER["password"]):
        logger.warning(f"Failed login — wrong password for username='{form_data.username}'")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": form_data.username})
    logger.info(f"Login successful for username='{form_data.username}'")
    return {"access_token": token, "token_type": "bearer"}