from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Transaction, Account
from ..schemas import DepositRequest, TransferRequest, AccountPublic
from ..services.banking import deposit, transfer

router = APIRouter(prefix="/transactions", tags=["Transações"])


def account_response(account):
    return AccountPublic(
        id=account.id,
        balance=Decimal(account.balance_cents) / 100,
    )


@router.post("/deposit")
def create_deposit(
    data: DepositRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = deposit(db, user.id, data.amount)
    return {
        "message": "Depósito realizado",
        "account": account_response(account),
    }


@router.post("/transfer")
def create_transfer(
    data: TransferRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = transfer(
        db,
        user.id,
        data.destination_account_id,
        data.amount,
    )
    return {
        "message": "Transferência realizada",
        "account": account_response(account),
    }


@router.get("/history")
def transaction_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter_by(user_id=user.id).first()
    if account is None:
        from fastapi import HTTPException

        raise HTTPException(404, "Conta não encontrada")

    transactions = (
        db.query(Transaction)
        .filter(
            (Transaction.sender_account_id == account.id)
            | (Transaction.receiver_account_id == account.id)
        )
        .order_by(Transaction.id.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": tx.id,
            "sender_account_id": tx.sender_account_id,
            "receiver_account_id": tx.receiver_account_id,
            "amount_cents": tx.amount_cents,
            "kind": tx.kind,
            "created_at": tx.created_at.isoformat(),
        }
        for tx in transactions
    ]
