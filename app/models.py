from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    __table_args__ = {"schema": "student_schema"} # Your Postgres schema name

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer)
    gpa = Column(Float)