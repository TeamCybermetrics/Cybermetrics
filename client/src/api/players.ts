import { apiClient } from "@/api/client";

export interface PlayerSearchResult {
  id: number;
  name: string;
  score: number;
  image_url: string;
  years_active: string;
}

export interface SavedPlayer {
  id: number;
  name: string;
  image_url?: string;
  years_active?: string;
  [key: string]: any; // Allow additional fields
}

export interface PlayerDetail {
  id: number;
  name: string;
  image_url: string;
  years_active?: string;
  first_name?: string;
  last_name?: string;
  mlb_played_first?: string;
  mlb_played_last?: string;
  key_retro?: string;
  key_bbref?: string;
  key_fangraphs?: number;
}

export interface AddPlayerResponse {
  message: string;
  player_id: string;
}

export interface DeletePlayerResponse {
  message: string;
}

export const playersApi = {
  search: async (query: string): Promise<PlayerSearchResult[]> => {
    return apiClient.get<PlayerSearchResult[]>(`/api/players/search?q=${encodeURIComponent(query)}`);
  },

  getDetail: async (playerId: number): Promise<PlayerDetail> => {
    return apiClient.get<PlayerDetail>(`/api/players/${playerId}/detail`);
  },

  getSaved: async (): Promise<SavedPlayer[]> => {
    return apiClient.get<SavedPlayer[]>("/api/players/saved");
  },

  addSaved: async (player: { id: number; name: string; image_url?: string; years_active?: string }): Promise<AddPlayerResponse> => {
    return apiClient.post<AddPlayerResponse>("/api/players/saved", player);
  },

  deleteSaved: async (playerId: number): Promise<DeletePlayerResponse> => {
    return apiClient.delete<DeletePlayerResponse>(`/api/players/saved/${playerId}`);
  },
};

