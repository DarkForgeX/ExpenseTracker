from fastapi import APIRouter, HTTPException
from psycopg import Error

from app.database import get_connection

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_analytics_summary():
    monthly_query = """
        SELECT
            COALESCE(SUM(amount), 0) AS total_spending,
            COUNT(*) AS expense_count
        FROM public.expenses
        WHERE expense_date >= DATE_TRUNC('month', CURRENT_DATE)::date
          AND expense_date < (
              DATE_TRUNC('month', CURRENT_DATE)
              + INTERVAL '1 month'
          )::date;
    """

    category_query = """
        SELECT
            category,
            SUM(amount) AS total
        FROM public.expenses
        WHERE expense_date >= DATE_TRUNC('month', CURRENT_DATE)::date
          AND expense_date < (
              DATE_TRUNC('month', CURRENT_DATE)
              + INTERVAL '1 month'
          )::date
        GROUP BY category
        ORDER BY total DESC;
    """

    recent_query = """
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
        ORDER BY expense_date DESC, created_at DESC
        LIMIT 5;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(monthly_query)
                monthly = cursor.fetchone()

                cursor.execute(category_query)
                categories = cursor.fetchall()

                cursor.execute(recent_query)
                recent_expenses = cursor.fetchall()

        return {
            "monthly_total": monthly["total_spending"],
            "monthly_count": monthly["expense_count"],
            "category_breakdown": categories,
            "recent_expenses": recent_expenses,
        }

    except Error as exc:
        import logging

        logging.getLogger(__name__).exception(
            "Database error while retrieving analytics"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve analytics",
        ) from exc
