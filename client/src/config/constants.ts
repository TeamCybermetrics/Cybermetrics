export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const STORAGE_KEYS = {
  AUTH_TOKEN: "auth_token",
  USER_ID: "user_id",
  USER_EMAIL: "user_email",
} as const;

export const ROUTES = {
  LANDING: "/",
  LOGIN: "/login",
  SIGNUP: "/signup",
  LINEUP_CONSTRUCTOR: "/lineup-constructor",
  ROSTER_CONSTRUCTOR: "/roster-constructor",
  OUR_ALGORITHM: "/our-algorithm",
} as const;
