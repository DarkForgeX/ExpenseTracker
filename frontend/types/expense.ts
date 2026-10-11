export const EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
    "Other",
] as const;

export const PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Card",
    "Bank Transfer",
    "Other",
] as const;

export type ExpenseCategory = (typeof EXPENSE_CATEGORIES)[number];
export type PaymentMethod = (typeof PAYMENT_METHODS)[number];
export type NumericValue = number | string;

export interface Expense {
    id: string;
    title: string;
    amount: NumericValue;
    category: string;
    payment_method: string;
    description: string | null;
    expense_date: string;
    created_at: string;
}

export interface ExpensePayload {
    title: string;
    amount: number;
    category: ExpenseCategory;
    payment_method: PaymentMethod;
    description?: string;
    expense_date: string;
}

export interface ExpenseUpdatePayload {
    title: string;
    amount: number;
    category: ExpenseCategory;
    payment_method: PaymentMethod;
    description?: string;
    expense_date: string;
}

export interface CategoryBreakdown {
    category: string;
    total: NumericValue;
}

export interface AnalyticsSummary {
    monthly_total: NumericValue;
    monthly_count: number;
    category_breakdown: CategoryBreakdown[];
    recent_expenses: Expense[];
}

export interface ExpenseFormValues {
    title: string;
    amount: string;
    category: ExpenseCategory;
    payment_method: PaymentMethod;
    expense_date: string;
    description: string;
}
