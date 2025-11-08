import { teamBuilderApi, SaveLineupPayload } from "@/api/teamBuilder";

export const teamBuilderActions = {
  fetchLineup: async () => {
    try {
      const data = await teamBuilderApi.getLineup();
      return { success: true as const, data };
    } catch (error) {
      return {
        success: false as const,
        error: error instanceof Error ? error.message : "Failed to load lineup",
      };
    }
  },

  saveLineup: async (payload: SaveLineupPayload) => {
    try {
      const data = await teamBuilderApi.saveLineup(payload);
      return { success: true as const, data };
    } catch (error) {
      return {
        success: false as const,
        error: error instanceof Error ? error.message : "Failed to save lineup",
      };
    }
  },

  deleteLineup: async () => {
    try {
      const data = await teamBuilderApi.deleteLineup();
      return { success: true as const, data };
    } catch (error) {
      return {
        success: false as const,
        error: error instanceof Error ? error.message : "Failed to delete lineup",
      };
    }
  },
};
