from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import ads_rout, users_rout, login_rout
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Advertisements Service API", version="1.0.0", lifespan=lifespan)

app.include_router(login_rout.router, tags=["Authentication"])
app.include_router(ads_rout.router, tags=["Advertisements"])
app.include_router(users_rout.router, tags=["Users"])


@app.get("/")
async def root():
    return {"message": "This is simple API"}
