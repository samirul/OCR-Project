from fastapi import APIRouter
from app.src.auth.router import router_auth as auth_user_router

router = APIRouter()

router.include_router(auth_user_router, prefix="/auth", tags=["Auth user router"])
