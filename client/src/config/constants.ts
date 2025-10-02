export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const STORAGE_KEYS = {
  AUTH_TOKEN: "auth_token",
  USER_ID: "user_id",
  USER_EMAIL: "user_email",
} as const;

