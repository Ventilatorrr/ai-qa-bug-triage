from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import create_tables
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.bugs import router as bugs_router
from app.api.ai_assist import router as ai_assist_router
from app.version import APP_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(version=APP_VERSION, lifespan=lifespan)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(bugs_router)
app.include_router(ai_assist_router)


@app.get("/version")
def get_version():
    return {"version": app.version}


app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)
