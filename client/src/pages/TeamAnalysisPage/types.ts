export type DiamondPosition = "LF" | "CF" | "RF" | "3B" | "SS" | "2B" | "1B" | "P" | "C" | "DH";

export type SavedPlayer = {
  id: number;
  name: string;
  image_url?: string;
  years_active?: string;
};

export type LineupState = Record<DiamondPosition, SavedPlayer | null>;

export type SavedTeam = {
  id: string;
  name: string;
  lineup: LineupState;
  savedAt: string;
};

export type TeamPlayer = SavedPlayer & { position: DiamondPosition };