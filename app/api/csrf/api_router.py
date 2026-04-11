from fastapi import APIRouter
from app.src.csrf.router import router_csrf

router = APIRouter()

router.include_router(router_csrf, prefix="/new", tags=["New csrf token"])
