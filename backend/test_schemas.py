from datetime import date
from decimal import Decimal

from app.schemas import ExpenseCreate


expense = ExpenseCreate(
    title="Lunch",
    amount=Decimal("250.00"),
    category="Food",
    payment_method="UPI",
    expense_date=date.today(),
)

print(expense.model_dump())
print("Schema validation successful!")
