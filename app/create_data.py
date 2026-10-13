import argparse
import random

from argon2 import PasswordHasher
from sqlalchemy.exc import SQLAlchemyError

from database import Base, SessionLocal, engine
from models import User, Account, Transaction

TEST_PASSWORD = "Lab@SecureBank2026!"
password_hasher = PasswordHasher()

TEST_USERS = [
    {"name": "Ana Silva", "email": "ana@securebank.local"},
    {"name": "Bruno Costa", "email": "bruno@securebank.local"},
    {"name": "Carla Souza", "email": "carla@securebank.local"},
    {"name": "Daniel Lima", "email": "daniel@securebank.local"},
    {"name": "Eva Santos", "email": "eva@securebank.local"},
]


def create_users_and_accounts(db):
    """Cria os usuários de teste e suas contas, sem duplicá-los."""

    accounts = []

    for data in TEST_USERS:
        user = db.query(User).filter(User.email == data["email"]).first()

        if user is None:
            user = User(
                name=data["name"],
                email=data["email"],
                password_hash=password_hasher.hash(TEST_PASSWORD),
                role="user",
            )
            db.add(user)
            db.flush()
            print(f"[USUÁRIO CRIADO] {user.email}")
        else:
            print(f"[USUÁRIO EXISTENTE] {user.email}")

        account = db.query(Account).filter(Account.user_id == user.id).first()

        if account is None:
            account = Account(
                user_id=user.id,
                balance_cents=100_000,  # R$ 1.000,00
            )
            db.add(account)
            db.flush()
            print(f"[CONTA CRIADA] Usuário: {user.email}")
        else:
            print(f"[CONTA EXISTENTE] Usuário: {user.email}")

        accounts.append(account)

    db.commit()
    return accounts


def simulate_deposit(db, account, amount_cents):
    """Simula um depósito e registra a transação."""

    account.balance_cents += amount_cents

    transaction = Transaction(
        sender_account_id=None,
        receiver_account_id=account.id,
        amount_cents=amount_cents,
        kind="deposit",
    )

    db.add(transaction)
    db.commit()

    print(f"[DEPÓSITO] Conta {account.id} recebeu " f"R$ {amount_cents / 100:.2f}")


def simulate_transfer(db, sender, receiver, amount_cents):
    """Transfere dinheiro entre contas na mesma transação SQL."""

    if sender.id == receiver.id:
        return False

    if sender.balance_cents < amount_cents:
        return False

    sender.balance_cents -= amount_cents
    receiver.balance_cents += amount_cents

    transaction = Transaction(
        sender_account_id=sender.id,
        receiver_account_id=receiver.id,
        amount_cents=amount_cents,
        kind="transfer",
    )

    db.add(transaction)
    db.commit()

    print(
        f"[TRANSFERÊNCIA] Conta {sender.id} -> Conta {receiver.id} | "
        f"R$ {amount_cents / 100:.2f}"
    )

    return True


def simulate_transactions(db, accounts, quantity):
    """Gera depósitos e transferências aleatórias."""

    if len(accounts) < 2:
        raise ValueError("São necessárias pelo menos duas contas.")

    completed = 0
    deposits = 0
    transfers = 0
    attempts = 0
    max_attempts = quantity * 3

    while completed < quantity and attempts < max_attempts:
        attempts += 1

        # Escolhe o tipo de operação.
        if random.random() < 0.25:
            account = random.choice(accounts)
            amount_cents = random.randint(1_000, 25_000)

            try:
                simulate_deposit(db, account, amount_cents)
                deposits += 1
                completed += 1
            except SQLAlchemyError:
                db.rollback()
                raise

        else:
            sender, receiver = random.sample(accounts, 2)
            amount_cents = random.randint(500, 15_000)

            try:
                if simulate_transfer(db, sender, receiver, amount_cents):
                    transfers += 1
                    completed += 1
            except SQLAlchemyError:
                db.rollback()
                raise

    print("\n=== RESUMO DA SIMULAÇÃO ===")
    print(f"Operações concluídas: {completed}")
    print(f"Depósitos: {deposits}")
    print(f"Transferências: {transfers}")

    if completed < quantity:
        print(
            "Aviso: não foi possível concluir todas as operações. "
            "Algumas transferências foram recusadas por saldo insuficiente."
        )


def show_balances(db, accounts):
    """Exibe os saldos finais das contas."""

    print("\n=== SALDOS FINAIS ===")

    for account in accounts:
        db.refresh(account)

        user = db.query(User).filter(User.id == account.user_id).first()

        print(
            f"{user.name:15} | Conta {account.id:3} | "
            f"Saldo: R$ {account.balance_cents / 100:,.2f}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Gera dados fictícios para a SecureBank API."
    )
    parser.add_argument(
        "--transactions",
        type=int,
        default=100,
        help="Quantidade de operações a simular (padrão: 100).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semente opcional para reproduzir a sequência aleatória.",
    )
    args = parser.parse_args()

    if args.transactions < 0:
        parser.error("--transactions não pode ser negativo.")

    # Evita executar acidentalmente contra um banco não local SQLite.
    if engine.dialect.name != "sqlite":
        raise RuntimeError("Este script de laboratório aceita somente SQLite.")

    if args.seed is not None:
        random.seed(args.seed)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        accounts = create_users_and_accounts(db)
        simulate_transactions(db, accounts, args.transactions)
        show_balances(db, accounts)

        print("\nCredencial de teste para os usuários novos:")
        print(f"Senha: {TEST_PASSWORD}")
        print("Use somente no ambiente local de laboratório.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
