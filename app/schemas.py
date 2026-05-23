from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Optional
import re

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    age: int = Field(..., ge=1, le=100)
    gpa: float = Field(..., ge=0.0, le=10.0)
    course: str = Field(..., min_length=2, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_be_letters(cls, v):
        if not re.match(r"^[A-Za-z\s]+$",v):
            raise ValueError("Name must contain only letters and spaces")
        return v.strip()
    
    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError("Email must be a valid email address")
        return v.lower().strip()
    
    @field_validator("gpa")
    @classmethod
    def gpa_must_be_valid(cls, v):
        return round(v,2)


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None,min_length=2, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    age: Optional[int] = Field(None,ge=1, le=100)
    gpa: Optional[float] =Field(None, ge=0.0, le=10.0)
    course: Optional[str] = Field(None, min_length=2, max_length=100) 

    @field_validator("name")
    @classmethod
    def name_must_be_letters(cls, v):
        if not re.match(r"^[A-Za-z\s]+$",v):
            raise ValueError("Name must contain only letters and spaces")
        return v.strip() if v else v
    
    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError("Email must be a valid email address")
        return v.lower().strip() if v else v

class StudentResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    age: Optional[int] = None
    gpa: Optional[float] = None
    course: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)