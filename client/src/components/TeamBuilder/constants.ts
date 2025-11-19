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
  LF: { top: "22%", left: "13%" },
  CF: { top: "12%", left: "50%" },
  RF: { top: "22%", left: "87%" },
  SS: { top: "38%", left: "34%" },
  "2B": { top: "38%", left: "68%" },
  "3B": { top: "48%", left: "12%" },
  "1B": { top: "48%", left: "88%" },
  C: { top: "75%", left: "50%" },
  DH: { top: "82%", left: "80%" },
};
export const staticSpots: Array<{ label: string; top: string; left: string }> = [];

