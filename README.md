# Learning Management System (LMS) API

A comprehensive Learning Management System built with FastAPI, implementing role-based access control (RBAC), JWT authentication, and RESTful API design principles using Screaming Architecture.

## Architecture: Screaming Architecture (Module-Based)

This project follows **Screaming Architecture** principles, where the folder structure immediately communicates what the application does:

```
wale/
├── apps/                    # Application modules
│   ├── users/              # User management module
│   │   ├── models.py       # User database model
│   │   ├── schemas.py      # User request/response schemas
│   │   ├── services.py     # User business logic & auth
│   │   └── routes.py       # User API endpoints
│   ├── auth/               # Authentication module
│   │   └── routes.py       # Login endpoints
│   ├── courses/            # Course management module
│   │   ├── models.py       # Course database model
│   │   ├── schemas.py      # Course schemas
│   │   └── routes.py       # Course API endpoints
│   └── enrollments/        # Enrollment management module
│       ├── models.py       # Enrollment database model
│       ├── schemas.py      # Enrollment schemas
│       └── routes.py       # Enrollment API endpoints
├── tests/                  # Comprehensive test suite
├── config.py              # Application configuration
├── database.py            # Database connection & session
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

### Why Screaming Architecture?

- **Self-documenting**: The structure tells you this is an LMS with users, courses, and enrollments
- **Module-based**: Each feature is a self-contained module
- **Easy navigation**: Find everything related to a feature in one place
- **Scalable**: Add new modules without affecting existing ones

## Features

### Core Entities

1. **User**
   - Fields: id, name, email, hashed_password, role (student/admin), is_active
   - Secure password hashing with bcrypt
   - Role-based access control

2. **Course**
   - Fields: id, title, code, capacity, is_active
   - Unique course codes
   - Capacity management
   - Active/inactive status

3. **Enrollment**
   - Fields: id, user_id, course_id, created_at
   - Student-course relationships
   - Automatic timestamp tracking

### Authentication & Authorization

- JWT-based authentication
- Role-based access control (RBAC)
  - Student role: Can view courses, enroll, and deregister
  - Admin role: Full course management and enrollment oversight

### Functional Requirements

#### User Management

- Register new users (student or admin)
- Login with JWT token generation
- Retrieve user profile (authenticated)
- Update user profile
- Email uniqueness validation
- Inactive users cannot authenticate

#### Course Management

- Retrieve all active courses (public) with filtering and pagination
- Search courses by title or code
- Filter courses by active status
- Retrieve course by ID (public)
- Create course (admin only)
- Update course details (admin only)
- Activate/deactivate courses (admin only)
- Delete (soft delete) courses (admin only)
- Unique course code validation
- Capacity validation (must be > 0)

#### Enrollment Management

- Enroll in course (students only)
- Deregister from course
- View my enrollments
- View all enrollments with filtering (admin only)
- Filter enrollments by user or course
- Prevent duplicate enrollments
- Prevent enrollment in full courses
- Prevent enrollment in inactive courses
- Admin oversight: view all enrollments
- Admin oversight: view course enrollments
- Admin oversight: remove students from courses

## Getting Started

### Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**

   ```bash
   cd /Users/ayomide/Desktop/ME/codebase/wale
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the contents from `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

   Update the values in `.env` as needed for your environment.

5. **Run the application**

   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive API Documentation (Swagger): http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## API Documentation

All API endpoints are fully documented with interactive examples in **Swagger UI**.

Visit http://localhost:8000/api/docs after starting the server to:

- View all available endpoints
- See request/response schemas
- Test endpoints directly from the browser
- View authentication requirements
- See example requests and responses

### Key Features

- **Pagination**: Most list endpoints support `skip` and `limit` parameters
- **Filtering**: Courses can be filtered by active status and searched by title/code
- **Search**: Case-insensitive search on courses
- **Metadata**: List responses include total count and pagination info

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v
```

All tests are passing with comprehensive coverage of:

- User registration and authentication
- Course CRUD operations
- Enrollment workflows
- Authorization checks (RBAC)
- Edge cases and error handling

## Security Features

- **Password Hashing**: Bcrypt with automatic salt generation
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions
- **Input Validation**: Pydantic schemas with validators
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Configurable cross-origin requests

## Database

- **ORM**: SQLAlchemy
- **Migrations**: Alembic (ready to use)
- **Default**: SQLite (for development)
- **Production**: PostgreSQL (recommended)

### Database Schema

See the Entity Relationship Diagram (ERD) below:

![Database Schema ERD](database_schema_erd.png)

**Key Relationships:**

- Users have many Enrollments (one-to-many)
- Courses have many Enrollments (one-to-many)
- Enrollments link Users and Courses (many-to-many through junction table)
- CASCADE delete on foreign keys ensures data integrity

## Business Rules

### User Management

- Email must be unique
- Role must be validated (student or admin)
- Inactive users cannot authenticate
- Passwords must be at least 6 characters

### Course Management

- Course code must be unique
- Capacity must be greater than zero
- Only admins can create/update/delete courses
- Soft delete (deactivation) for courses

### Enrollment Management

- Only authenticated students can enroll
- Cannot enroll in the same course twice
- Cannot enroll if course is full
- Cannot enroll if course is inactive
- Admins can view all enrollments
- Admins can remove students from courses

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy + SQLite/PostgreSQL
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib with bcrypt
- **Validation**: Pydantic
- **Testing**: Pytest
- **ASGI Server**: Uvicorn

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:

- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error or business rule violation
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid request data

## Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/lms_production
SECRET_KEY=<generate-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Future Enhancements

- Database migrations with Alembic
- Email verification
- Password reset functionality
- Course categories and tags
- Student grades and assignments
- File uploads for course materials
- Real-time notifications
- Analytics dashboard
- API rate limiting
- Caching with Redis

## Contributing

This is a capstone project for AltSchool Africa Backend Engineering.

## License

MIT License

## Acknowledgments

- AltSchool Africa
- FastAPI Documentation
- SQLAlchemy Documentation
