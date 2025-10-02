import { playersApi } from "@/api/players";

export const playerActions = {
  searchPlayers: async (query: string) => {
    try {
      const results = await playersApi.search(query);
      return { success: true, data: results };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Search failed",
      };
    }
  },

  getPlayerDetail: async (playerId: number) => {
    try {
      const detail = await playersApi.getDetail(playerId);
      return { success: true, data: detail };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to fetch player details",
      };
    }
  },

  getSavedPlayers: async () => {
    try {
      const players = await playersApi.getSaved();
      return { success: true, data: players };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to fetch saved players",
      };
    }
  },

  addPlayer: async (player: { id: number; name: string; image_url?: string; years_active?: string }) => {
    try {
      const response = await playersApi.addSaved(player);
      return { success: true, data: response };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to add player",
      };
    }
  },

  deletePlayer: async (playerId: number) => {
    try {
      const response = await playersApi.deleteSaved(playerId);
      return { success: true, data: response };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to delete player",
      };
    }
  },
};

