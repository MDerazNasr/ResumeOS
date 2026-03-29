from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.resumes import router as resumes_router
from app.db.database import initialize_database
from app.services.auth import DEV_USER
from app.services.resumes import ensure_dev_user_exists


app = FastAPI(title="ResumeOS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(resumes_router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()
    ensure_dev_user_exists(DEV_USER.id, DEV_USER.email, DEV_USER.name)

