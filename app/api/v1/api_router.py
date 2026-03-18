from fastapi import APIRouter
from app.src.auth.router import router_v1 as auth_v1

v1_router = APIRouter()

v1_router.include_router(auth_v1, prefix="/auth", tags=["Auth V1"])