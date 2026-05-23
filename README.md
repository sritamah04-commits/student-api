# Student API

A production-ready REST API built with Python FastAPI and PostgreSQL for managing student records. Built as a learning project covering REST services, database integration, JWT authentication, validation, logging, pagination, sorting, filtering and unit testing.

## Tech Stack

- **Python 3.11**
- **FastAPI** — modern web framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — database ORM
- **Pydantic V2** — data validation
- **JWT** — authentication
- **Uvicorn** — ASGI server
- **Pytest** — unit testing


## Features

- **CRUD Operations** — Create, Read, Update, Delete students
- **JWT Authentication** — POST, PUT, DELETE endpoints are protected
- **Input Validation** — Name, email, age, GPA, course all validated
- **Exception Handling** — Clean error messages with proper HTTP status codes
- **Logging** — Every request, warning and error logged to daily log files
- **Pagination** — Control page number and page size
- **Filtering** — Filter by course, age range, GPA range, name search
- **Sorting** — Sort by any field in ascending or descending order
- **Unit Tests** — 27 tests covering all endpoints and edge cases

