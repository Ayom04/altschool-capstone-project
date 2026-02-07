from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apps.config.database import Base, engine
from apps.config.config import get_settings
from datetime import datetime
from sqlalchemy import text
import time

from apps.users.models import User
from apps.courses.models import Course
from apps.enrollments.models import Enrollment

from apps.auth.routes import router as auth_router
from apps.users.routes import router as users_router
from apps.courses.routes import router as courses_router
from apps.enrollments.routes import router as enrollments_router
from apps.common.responses import success_response

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

app.openapi_schema = None


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=settings.app_name,
        version="1.0.0",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.state.start_time = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(enrollments_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        field = error.get("loc")[-1]
        msg = error.get("msg")
        error_messages.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation failed",
            "data": {"errors": error_messages}
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "data": None
        },
    )


@app.get("/")
def read_root():
    return success_response(
        data={"docs": "/api/docs", "version": "1.0.0"},
        message="Welcome to the LMS API"
    )


@app.get("/health")
def health_check():
    uptime_seconds = time.time() - app.state.start_time
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return success_response(
        data={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime": round(uptime_seconds, 2),
            "environment": "development" if settings.debug else "production",
            "database": {
                "status": db_status,
                "url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "sqlite"
            },
            "version": "1.0.0"
        },
        message="System is healthy"
    )
