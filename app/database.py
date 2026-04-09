from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # Reads your .env file

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the actual connection to your PostgreSQL database
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory — each time we call it, we get a fresh DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all our database models will inherit from
Base = declarative_base()

# This is a dependency — it gives a DB session to each request, then closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()