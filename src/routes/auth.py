from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Security,
    BackgroundTasks,
    Request,
    status,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.connect_db import get_session
from src.schemas.users import (
    UserModel,
    UserRequestEmail,
    UserPasswordResetConfirmationModel,
    UserResponse,
)
from src.schemas.tokens import TokenModel, TokenPasswordResetConfirmationModel
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import (
    send_email_for_verification,
    send_email_for_password_reset,
)


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    session: Session = Depends(get_session),
):
    user = await repository_users.get_user_by_email(body.email, session)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    user = await repository_users.create_user(body, session)
    background_tasks.add_task(
        send_email_for_verification, user.email, user.username, request.base_url
    )
    return {
        "user": user,
        "detail": "The user successfully created. Check your email for confirmation",
    }


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = await repository_users.get_user_by_email(body.username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.is_email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The email is not confirmed",
        )
    if not user.is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password reset is not confirmed",
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWTs
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, session)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    session: Session = Depends(get_session),
):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if user.refresh_token != token:
        await repository_users.update_token(user, None, session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, session)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/verification_email")
async def request_verification_email(
    body: UserRequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    session: Session = Depends(get_session),
):
    user = await repository_users.get_user_by_email(body.email, session)
    if user:
        if user.is_email_confirmed:
            return {"message": "The email is already confirmed"}
        if user.is_password_valid:
            background_tasks.add_task(
                send_email_for_verification, user.email, user.username, request.base_url
            )
    return {"message": "Check your email for confirmation"}


@router.get("/confirm_email/{token}")
async def confirm_email(token: str, session: Session = Depends(get_session)):
    email = await auth_service.decode_email_verification_token(token)
    user = await repository_users.get_user_by_email(email, session)
    if user is None or not user.is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.is_email_confirmed:
        return {"message": "The email is already confirmed"}
    await repository_users.confirm_email(email, session)
    return {"message": "Email confirmed"}


@router.post("/password_reset_email")
async def request_password_reset_email(
    body: UserRequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    session: Session = Depends(get_session),
):
    user = await repository_users.get_user_by_email(body.email, session)
    if user and user.is_email_confirmed:
        background_tasks.add_task(
            send_email_for_password_reset,
            user.email,
            user.username,
            request.base_url,
        )
    return {"message": "Check your email for a password reset"}


@router.get(
    "/reset_password/{token}", response_model=TokenPasswordResetConfirmationModel
)
async def reset_password(
    token: str,
    session: Session = Depends(get_session),
):
    email = await auth_service.decode_password_reset_token(token)
    user = await repository_users.get_user_by_email(email, session)
    if user is None or not user.is_email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset error"
        )
    if user.is_password_valid:
        await repository_users.invalidate_password(email, session)
    password_reset_confirmation_token = (
        await auth_service.create_password_reset_confirmation_token(data={"sub": email})
    )
    return {"password_reset_confirmation_token": password_reset_confirmation_token}


@router.patch("/reset_password_confirmation/{token}")
async def reset_password_confirmation(
    token: str,
    body: UserPasswordResetConfirmationModel,
    session: Session = Depends(get_session),
):
    email = await auth_service.decode_password_reset_confirmation_token(token)
    user = await repository_users.get_user_by_email(email, session)
    if user is None or not user.is_email_confirmed or user.is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset confirmation error",
        )
    body.password = auth_service.get_password_hash(body.password)
    await repository_users.reset_password(email, body.password, session)
    return {"message": "The password has been reset"}
