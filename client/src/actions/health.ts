import { healthApi, HealthResponse } from "@/api/health";

export const healthActions = {
  checkHealth: async (): Promise<
    { success: true; data: HealthResponse } | { success: false; error: string }
  > => {
    try {
      const response = await healthApi.check();
      return { success: true, data: response };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Health check failed",
      };
    }
  },
};

