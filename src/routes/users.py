from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.connect_db import get_session
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserDb,
    description="No more than 1 request per second",
    dependencies=[Depends(RateLimiter(times=1, seconds=1))],
)
async def read_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch(
    "/avatar",
    response_model=UserDb,
    description="No more than 2 requests per 5 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    session: Session = Depends(get_session),
):
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    try:
        r = cloudinary.uploader.upload(
            file.file, public_id=f"ContactsAPI/{current_user.username}", overwrite=True
        )
        src_url = cloudinary.CloudinaryImage(
            f"ContactsAPI/{current_user.username}"
        ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    except Exception as error_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload image error: {str(error_message)}",
        )
    user = await repository_users.update_avatar(current_user.email, src_url, session)
    return user
