import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from src.database.connect_db import get_session
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.users import UserDb


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch("/avatar", response_model=UserDb)
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
    api_name = settings.api_name.replace(" ", "_")
    try:
        r = cloudinary.uploader.upload(
            file.file,
            public_id=f"{api_name}/{current_user.username}",
            overwrite=True,
        )
        src_url = cloudinary.CloudinaryImage(
            f"{api_name}/{current_user.username}"
        ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    except Exception as error_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload image error: {str(error_message)}",
        )
    user = await repository_users.update_avatar(current_user.email, src_url, session)
    return user
