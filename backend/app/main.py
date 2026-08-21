from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}

app.include_router(router)