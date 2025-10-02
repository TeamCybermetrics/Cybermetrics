import { apiClient } from "@/api/client";

export interface HealthResponse {
  status: string;
  firebase_connected: boolean;
}

export const healthApi = {
  check: async (): Promise<HealthResponse> => {
    return apiClient.get<HealthResponse>("/health");
  },
};

