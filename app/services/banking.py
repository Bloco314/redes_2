from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Account, Transaction, SecurityLog


def to_cents(amount: Decimal) -> int:
    normalized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if normalized != amount or normalized <= 0:
        raise HTTPException(422, "Valor monetário inválido")
    return int(normalized * 100)


def audit(
    db: Session,
    event: str,
    user_id: int | None,
    details: str = "",
):
    db.add(
        SecurityLog(
            event=event,
            user_id=user_id,
            details=details[:500],
        )
    )


def get_owned_account(db: Session, user_id: int) -> Account:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if account is None:
        raise HTTPException(404, "Conta não encontrada")
    return account


def deposit(db: Session, user_id: int, amount: Decimal):
    cents = to_cents(amount)
    account = get_owned_account(db, user_id)

    try:
        account.balance_cents += cents
        db.add(
            Transaction(
                sender_account_id=None,
                receiver_account_id=account.id,
                amount_cents=cents,
                kind="deposit",
            )
        )
        audit(db, "deposit_success", user_id, f"amount_cents={cents}")
        db.commit()
        db.refresh(account)
        return account
    except Exception:
        db.rollback()
        raise


def transfer(
    db: Session,
    user_id: int,
    destination_account_id: int,
    amount: Decimal,
):
    cents = to_cents(amount)
    source = get_owned_account(db, user_id)

    destination = db.get(Account, destination_account_id)

    if destination is None:
        raise HTTPException(404, "Conta de destino não encontrada")
    if source.id == destination.id:
        raise HTTPException(422, "Transferência para a própria conta")
    if source.balance_cents < cents:
        raise HTTPException(422, "Saldo insuficiente")

    try:
        source.balance_cents -= cents
        destination.balance_cents += cents

        db.add(
            Transaction(
                sender_account_id=source.id,
                receiver_account_id=destination.id,
                amount_cents=cents,
                kind="transfer",
            )
        )
        audit(db, "transfer_success", user_id, f"amount_cents={cents}")
        db.commit()
        db.refresh(source)
        return source
    except Exception:
        db.rollback()
        raise
