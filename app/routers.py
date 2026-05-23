from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import asc, desc
from typing import Optional
from app import models
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.database import get_db
from app.auth import get_current_user
from app.logger import logger

router = APIRouter(prefix="/students", tags=["Students"])


# GET /students — get all students with pagination, filtering and sorting
@router.get("/", response_model=list[StudentResponse])
def get_all_students(
    db: Session = Depends(get_db),

    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Students per page"),

    # Filtering
    course: Optional[str] = Query(None, description="Filter by course name"),
    search: Optional[str] = Query(None, description="Search by student name"),
    min_age: Optional[int] = Query(None, ge=1, description="Minimum age"),
    max_age: Optional[int] = Query(None, le=100, description="Maximum age"),
    min_gpa: Optional[float] = Query(None, ge=0.0, description="Minimum GPA"),
    max_gpa: Optional[float] = Query(None, le=10.0, description="Maximum GPA"),

    # Sorting
    sort_by: Optional[str] = Query(
        None,
        description="Field to sort by — name, age, gpa, course"
    ),
    order: Optional[str] = Query(
        "asc",
        description="Sort direction — asc or desc"
    )
):
    try:
        logger.info(
            f"Fetching students — page={page}, size={size}, "
            f"course={course}, search={search}, "
            f"min_age={min_age}, max_age={max_age}, "
            f"min_gpa={min_gpa}, max_gpa={max_gpa}, "
            f"sort_by={sort_by}, order={order}"
        )

        # Start with base query
        query = db.query(models.Student)

        # ── FILTERING ──────────────────────────────────────────

        # Filter by exact course name (case insensitive)
        if course:
            query = query.filter(
                models.Student.course.ilike(f"%{course}%")
            )

        # Search by name (partial match, case insensitive)
        if search:
            query = query.filter(
                models.Student.name.ilike(f"%{search}%")
            )

        # Filter by minimum age
        if min_age is not None:
            query = query.filter(models.Student.age >= min_age)

        # Filter by maximum age
        if max_age is not None:
            query = query.filter(models.Student.age <= max_age)

        # Filter by minimum GPA
        if min_gpa is not None:
            query = query.filter(models.Student.gpa >= min_gpa)

        # Filter by maximum GPA
        if max_gpa is not None:
            query = query.filter(models.Student.gpa <= max_gpa)

        # ── SORTING ────────────────────────────────────────────

        # Allowed fields to sort by — prevents SQL injection
        allowed_sort_fields = {
            "name": models.Student.name,
            "age": models.Student.age,
            "gpa": models.Student.gpa,
            "course": models.Student.course,
            "id": models.Student.id
        }

        if sort_by:
            if sort_by not in allowed_sort_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid sort field '{sort_by}'. Allowed fields: {list(allowed_sort_fields.keys())}"
                )
            sort_column = allowed_sort_fields[sort_by]
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        # ── PAGINATION ─────────────────────────────────────────

        total = query.count()
        skip = (page - 1) * size
        students = query.offset(skip).limit(size).all()

        logger.info(f"Returned {len(students)} of {total} total students")
        return students

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching students: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")


# GET /students/{id} — get one student
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching student with id={student_id}")
        student = db.query(models.Student).filter(
            models.Student.id == student_id
        ).first()
        if not student:
            logger.warning(f"Student id={student_id} not found")
            raise HTTPException(status_code=404, detail="Student not found")
        logger.info(f"Student id={student_id} fetched successfully")
        return student
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching student id={student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")


# POST /students — create student
@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"User '{current_user}' creating student with email={student.email}")
        new_student = models.Student(**student.model_dump())
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        logger.info(f"Student created successfully with id={new_student.id}")
        return new_student
    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate email attempted: {student.email}")
        raise HTTPException(status_code=400, detail="Email already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating student: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")


# PUT /students/{id} — update student
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    updates: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"User '{current_user}' updating student id={student_id}")
        student = db.query(models.Student).filter(
            models.Student.id == student_id
        ).first()
        if not student:
            logger.warning(f"Student id={student_id} not found for update")
            raise HTTPException(status_code=404, detail="Student not found")
        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(student, field, value)
        db.commit()
        db.refresh(student)
        logger.info(f"Student id={student_id} updated successfully")
        return student
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate email on update for student id={student_id}")
        raise HTTPException(status_code=400, detail="Email already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating student id={student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")


# DELETE /students/{id} — delete student
@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"User '{current_user}' deleting student id={student_id}")
        student = db.query(models.Student).filter(
            models.Student.id == student_id
        ).first()
        if not student:
            logger.warning(f"Student id={student_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Student not found")
        db.delete(student)
        db.commit()
        logger.info(f"Student id={student_id} deleted successfully")
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting student id={student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")