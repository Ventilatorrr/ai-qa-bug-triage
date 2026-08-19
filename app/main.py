from fastapi import FastAPI

from app.database import create_tables
from app.api.auth import router as auth_router


create_tables()

app = FastAPI()

app.include_router(auth_router)
