from app.database import get_connection


def main():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    current_database() AS database_name,
                    NOW() AS server_time,
                    COUNT(*) AS expense_count
                FROM public.expenses
                """
            )

            result = cursor.fetchone()

            print("Database connection successful!")
            print(f"Database: {result['database_name']}")
            print(f"Server time: {result['server_time']}")
            print(f"Expense count: {result['expense_count']}")


if __name__ == "__main__":
    main()
    