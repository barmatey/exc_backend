from fastapi import Depends, FastAPI, APIRouter

from .db import User, create_db_and_tables
from .schema import UserCreate, UserRead, UserUpdate
from .user import auth_backend, current_active_user, fastapi_users

router_auth = APIRouter()
router_auth.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router_auth.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router_auth.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router_auth.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router_auth.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
