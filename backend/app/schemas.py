from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ExpenseCategory = Literal[
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
    "Other",
]

PaymentMethod = Literal[
    "Cash",
    "UPI",
    "Card",
    "Bank Transfer",
    "Other",
]


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: ExpenseCategory
    payment_method: PaymentMethod
    description: str | None = Field(default=None, max_length=1000)
    expense_date: date


class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    category: ExpenseCategory | None = None
    payment_method: PaymentMethod | None = None
    description: str | None = Field(default=None, max_length=1000)
    expense_date: date | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    amount: Decimal
    category: str
    payment_method: str
    description: str | None
    expense_date: date
    created_at: datetime
