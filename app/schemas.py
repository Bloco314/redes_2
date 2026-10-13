from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountPublic(BaseModel):
    id: int
    balance: Decimal


class DepositRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class TransferRequest(BaseModel):
    destination_account_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class TransactionPublic(BaseModel):
    id: int
    sender_account_id: int | None
    receiver_account_id: int
    amount_cents: int
    kind: str
    created_at: str
