import os
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.exceptions.exception import http_exception_handler, validation_exception_handler
# from app.api.v1.api_router import v1_router

from app.api.auth.api_router import  router as user_router


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=str(os.environ.get('SECRET_KEY')))
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

origins = ["http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(v1_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/user")

@app.get("/")
async def root():
    return {"status": "API is up and running!"}