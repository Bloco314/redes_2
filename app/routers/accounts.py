from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import UserPublic, AccountPublic
from ..services.banking import get_owned_account

router = APIRouter(tags=["Contas"])


@router.get("/users/me", response_model=UserPublic)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/accounts/me", response_model=AccountPublic)
def get_my_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = get_owned_account(db, user.id)
    return AccountPublic(
        id=account.id,
        balance=Decimal(account.balance_cents) / 100,
    )
