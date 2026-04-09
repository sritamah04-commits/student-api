from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str
    age: int
    gpa: float
    course: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gpa: Optional[float] = None
    course: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    age: Optional[int] = None
    gpa: Optional[float] = None
    course: Optional[str] = None

    class Config:
        from_attributes = True
