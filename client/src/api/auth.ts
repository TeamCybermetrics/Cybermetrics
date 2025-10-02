import { apiClient } from "@/api/client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  user_id: string;
  email: string;
  token: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  display_name?: string | null;
}

export interface SignupResponse {
  message: string;
  user_id: string;
  email: string;
}

export interface VerifyTokenResponse {
  message: string;
  user_id: string;
  email: string;
}

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    return apiClient.post<LoginResponse>("/api/auth/login", credentials);
  },

  signup: async (userData: SignupRequest): Promise<SignupResponse> => {
    return apiClient.post<SignupResponse>("/api/auth/signup", userData);
  },

  verifyToken: async (): Promise<VerifyTokenResponse> => {
    return apiClient.get<VerifyTokenResponse>("/api/auth/verify");
  },
};

