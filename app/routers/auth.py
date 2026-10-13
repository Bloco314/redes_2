from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models import User, Account, SecurityLog
from ..schemas import UserRegister, UserPublic, LoginRequest, TokenResponse
from ..security import hash_password, verify_password, create_access_token
from ..defense.rate_limit import login_limiter

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserPublic, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    user = User(
        name=data.name.strip(),
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
    )

    try:
        db.add(user)
        db.flush()

        db.add(Account(user_id=user.id, balance_cents=0))
        db.add(
            SecurityLog(
                event="register_success",
                user_id=user.id,
            )
        )
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível cadastrar esse e-mail",
        )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = str(data.email).lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(
        data.password,
        user.password_hash if user else "$invalid$",
    ):
        db.add(
            SecurityLog(
                event="login_failed",
                user_id=user.id if user else None,
                ip_address=request.client.host if request.client else None,
                details="Credenciais inválidas",
            )
        )
        db.commit()
        raise HTTPException(401, "E-mail ou senha inválidos")

    db.add(
        SecurityLog(
            event="login_success",
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login-secure", response_model=TokenResponse)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "unknown"
    if not login_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas. Tente novamente mais tarde.",
            headers={"Retry-After": "60"},
        )

    email = str(data.email).lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(
        data.password,
        user.password_hash if user else "$invalid$",
    ):
        db.add(
            SecurityLog(
                event="login_failed",
                user_id=user.id if user else None,
                ip_address=request.client.host if request.client else None,
                details="Credenciais inválidas",
            )
        )
        db.commit()
        raise HTTPException(401, "E-mail ou senha inválidos")

    db.add(
        SecurityLog(
            event="login_success",
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    return TokenResponse(access_token=create_access_token(user.id))
