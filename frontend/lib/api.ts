import type {
  AnalyticsSummary,
  Expense,
  ExpensePayload,
  ExpenseUpdatePayload,
} from "@/types/expense";

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store",
    });
  } catch {
    throw new Error("Unable to reach the ExpenseFlow API.");
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // Keep the status-based message when the API has no JSON error body.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  listExpenses: (params?: { category?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.category) query.set("category", params.category);
    if (params?.search) query.set("search", params.search);
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return request<Expense[]>(`/expenses${suffix}`);
  },
  getAnalytics: () => request<AnalyticsSummary>("/analytics/summary"),
  createExpense: (payload: ExpensePayload) =>
    request<Expense>("/expenses", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateExpense: (id: string, payload: ExpenseUpdatePayload) =>
    request<Expense>(`/expenses/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteExpense: (id: string) =>
    request<void>(`/expenses/${id}`, { method: "DELETE" }),
};
