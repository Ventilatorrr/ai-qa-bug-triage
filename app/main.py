from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import create_tables
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router


app = FastAPI()

create_tables()

app.include_router(auth_router)
app.include_router(projects_router)

app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)