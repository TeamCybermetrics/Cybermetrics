import { SavedPlayer } from "@/api/players";

export type DiamondPosition =
  | "LF"
  | "CF"
  | "RF"
  | "3B"
  | "SS"
  | "2B"
  | "1B"
  | "C"
  | "DH";

export type LineupState = Record<DiamondPosition, SavedPlayer | null>;

export type SavedTeam = {
  id: string;
  name: string;
  lineup: LineupState;
  savedAt: string;
};

export const positionOrder: DiamondPosition[] = [
  "LF",
  "CF",
  "RF",
  "3B",
  "SS",
  "2B",
  "1B",
  "C",
  "DH",
];

export const positionCoordinates: Record<
  DiamondPosition,
  { top: string; left: string }
> = {
  // LF: { top: "16.25%", left: "25.5%" }
  LF: { top: "28%", left: "20%" },
  CF: { top: "18%", left: "50%" },
  RF: { top: "28%", left: "80%" },
  SS: { top: "48%", left: "38%" },
  "2B": { top: "48%", left: "62%" },
  "3B": { top: "66%", left: "26%" },
  "1B": { top: "66%", left: "74%" },
  C: { top: "90%", left: "50%" },
  DH: { top: "82%", left: "80%" },
};
export const staticSpots: Array<{ label: string; top: string; left: string }> = [];

