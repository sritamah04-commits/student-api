from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])


# GET all — public, no token needed
@router.get("/", response_model=list[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students


# GET one — public, no token needed
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# POST — protected, token required
@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# PUT — protected, token required
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    updates: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


# DELETE — protected, token required
@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()