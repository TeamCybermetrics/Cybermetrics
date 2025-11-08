import { apiClient } from "@/api/client";
import { SavedPlayer } from "@/api/players";

export type DiamondPosition = "LF" | "CF" | "RF" | "3B" | "SS" | "2B" | "1B" | "P" | "C" | "DH";

export interface LineupSlotPayload {
  player_id: number;
  name?: string;
  image_url?: string;
  years_active?: string;
}

export type LineupPayload = Record<DiamondPosition, LineupSlotPayload | null>;

export interface LineupFiltersPayload {
  salary_range: [number, number];
  selected_positions: DiamondPosition[];
}

export interface SaveLineupPayload {
  name: string;
  lineup: LineupPayload;
  filters: LineupFiltersPayload;
  team_score?: number;
  team_budget?: number;
  notes?: string;
}

export interface SavedLineup {
  id: string;
  name: string;
  lineup: LineupPayload;
  filters: LineupFiltersPayload;
  team_score?: number;
  team_budget?: number;
  notes?: string;
  saved_at: string;
  updated_at: string;
}

export interface LineupResponse {
  lineup: SavedLineup | null;
}

export interface DeleteLineupResponse {
  message: string;
}

export const teamBuilderApi = {
  getLineup: async (): Promise<LineupResponse> => {
    return apiClient.get<LineupResponse>("/api/team-builder/lineup");
  },

  saveLineup: async (payload: SaveLineupPayload): Promise<LineupResponse> => {
    return apiClient.post<LineupResponse>("/api/team-builder/lineup", payload);
  },

  deleteLineup: async (): Promise<DeleteLineupResponse> => {
    return apiClient.delete<DeleteLineupResponse>("/api/team-builder/lineup");
  },
};

export const buildLineupPayload = (
  lineupState: Record<DiamondPosition, SavedPlayer | null>,
  filters: LineupFiltersPayload,
  name: string
): SaveLineupPayload => {
  const payload: LineupPayload = Object.keys(lineupState).reduce((acc, key) => {
    const position = key as DiamondPosition;
    const player = lineupState[position];
    acc[position] = player
      ? {
          player_id: player.id,
          name: player.name,
          image_url: player.image_url,
          years_active: player.years_active,
        }
      : null;
    return acc;
  }, {} as LineupPayload);

  return {
    name,
    lineup: payload,
    filters,
  };
};
