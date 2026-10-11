import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status
from psycopg import Error, sql

from app.database import get_connection
from app.schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# CREATE EXPENSE
@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(expense: ExpenseCreate):
    query = """
        INSERT INTO public.expenses (
            title,
            amount,
            category,
            payment_method,
            description,
            expense_date
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING
            id, title, amount, category, payment_method,
            description, expense_date, created_at
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        expense.title.strip(),
                        expense.amount,
                        expense.category,
                        expense.payment_method,
                        expense.description,
                        expense.expense_date,
                    ),
                )
                created_expense = cursor.fetchone()

        return created_expense

    except Error as exc:
        logger.exception("Database error while creating expense")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create expense",
        ) from exc


# LIST EXPENSES
# LIST EXPENSES
@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    category: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=150),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    conditions = []
    params = []

    if category and category.strip():
        conditions.append("category = %s")
        params.append(category.strip())

    if search and search.strip():
        conditions.append(
            """
            (
                title ILIKE %s
                OR COALESCE(description, '') ILIKE %s
            )
            """
        )

        search_pattern = f"%{search.strip()}%"
        params.extend([search_pattern, search_pattern])

    query = """
        SELECT
            id,
            title,
            amount,
            category,
            payment_method,
            description,
            expense_date,
            created_at
        FROM public.expenses
    """

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        ORDER BY expense_date DESC, created_at DESC
        LIMIT %s OFFSET %s
    """

    params.extend([limit, offset])

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                expenses = cursor.fetchall()

        return expenses

    except Error as exc:
        logger.exception("Database error while listing expenses")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve expenses",
        ) from exc


# GET A SINGLE EXPENSE
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: UUID):
    query = """
        SELECT
            id, title, amount, category, payment_method,
            description, expense_date, created_at
        FROM public.expenses
        WHERE id = %s
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (expense_id,))
                expense = cursor.fetchone()

        if expense is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        return expense

    except HTTPException:
        raise

    except Error as exc:
        logger.exception("Database error while retrieving expense")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve expense",
        ) from exc


# UPDATE EXPENSE
@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: UUID, expense: ExpenseUpdate):
    updates = expense.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update",
        )

    if "title" in updates and updates["title"] is not None:
        updates["title"] = updates["title"].strip()

        if not updates["title"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Title cannot be empty",
            )

    allowed_columns = {
        "title",
        "amount",
        "category",
        "payment_method",
        "description",
        "expense_date",
    }

    invalid_columns = set(updates) - allowed_columns

    if invalid_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid fields",
        )

    assignments = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(column)) for column in updates
    )

    query = sql.SQL("""
        UPDATE public.expenses
        SET {}
        WHERE id = %s
        RETURNING
            id, title, amount, category, payment_method,
            description, expense_date, created_at
    """).format(assignments)

    values = list(updates.values()) + [expense_id]

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                updated_expense = cursor.fetchone()

        if updated_expense is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        return updated_expense

    except HTTPException:
        raise

    except Error as exc:
        logger.exception("Database error while updating expense")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update expense",
        ) from exc


# DELETE EXPENSE
@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(expense_id: UUID):
    query = """
        DELETE FROM public.expenses
        WHERE id = %s
        RETURNING id
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (expense_id,))
                deleted_expense = cursor.fetchone()

        if deleted_expense is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise

    except Error as exc:
        logger.exception("Database error while deleting expense")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete expense",
        ) from exc
