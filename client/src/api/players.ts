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

export interface SeasonStats {
  // Basic counting stats
  games: number;
  plate_appearances: number;
  at_bats: number;
  hits: number;
  singles: number;
  doubles: number;
  triples: number;
  home_runs: number;
  runs: number;
  rbi: number;
  walks: number;
  strikeouts: number;
  stolen_bases: number;
  caught_stealing: number;
  
  // Rate stats
  batting_average: number;
  on_base_percentage: number;
  slugging_percentage: number;
  ops: number;
  isolated_power: number;
  babip: number;
  
  // Plate discipline
  walk_rate: number;
  strikeout_rate: number;
  bb_k_ratio: number;
  
  // Advanced metrics
  woba: number;
  wrc_plus: number;
  war: number;
  off: number;
  def_: number;
  base_running: number;
  
  // Contact quality (may be null for older seasons)
  hard_hit_rate?: number | null;
  barrel_rate?: number | null;
  avg_exit_velocity?: number | null;
  avg_launch_angle?: number | null;
  
  // Team
  team_abbrev?: string | null;
}

export interface PlayerDetail {
  mlbam_id: number;
  fangraphs_id: number;
  name: string;
  image_url: string;
  years_active: string;
  team_abbrev?: string | null;
  overall_score: number;
  seasons: Record<string, SeasonStats>;  // Year -> Stats mapping
}

export interface AddPlayerResponse {
  message: string;
  player_id: string;
}

export interface DeletePlayerResponse {
  message: string;
}

export interface TeamWeaknessResponse {
  strikeout_rate: number;
  walk_rate: number;
  isolated_power: number;
  on_base_percentage: number;
  base_running: number;
}

export interface PlayerValueScore {
  id: number;
  name: string;
  adjustment_score: number;
  value_score: number;
}

export const playersApi = {
  search: async (query: string, signal?: AbortSignal): Promise<PlayerSearchResult[]> => {
    return apiClient.get<PlayerSearchResult[]>(`/api/players/search?q=${encodeURIComponent(query)}`, {
      signal
    });
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

  getTeamWeakness: async (playerIds: number[]): Promise<TeamWeaknessResponse> => {
    return apiClient.post<TeamWeaknessResponse>("/api/players/roster-averages/weakness", {
      player_ids: playerIds
    });
  },

  getPlayerValueScores: async (playerIds: number[]): Promise<PlayerValueScore[]> => {
    return apiClient.post<PlayerValueScore[]>("/api/players/value-scores", {
      player_ids: playerIds
    });
  },
};
