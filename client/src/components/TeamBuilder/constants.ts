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
  LF: { top: "21%", left: "20%" },
  CF: { top: "9%", left: "50%" },
  RF: { top: "21%", left: "80%" },
  SS: { top: "41%", left: "32.5%" },
  "2B": { top: "41%", left: "67.5%" },
  "3B": { top: "54%", left: "15%" },
  "1B": { top: "54%", left: "85%" },
  C: { top: "85%", left: "50%" },
  DH: { top: "82%", left: "80%" },
};
export const staticSpots: Array<{ label: string; top: string; left: string }> = [];

