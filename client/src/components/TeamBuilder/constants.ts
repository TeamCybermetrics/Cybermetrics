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
  LF: { top: "16%", left: "13%" },
  CF: { top: "8%", left: "50%" },
  RF: { top: "16%", left: "87%" },
  SS: { top: "38%", left: "32%" },
  "2B": { top: "38%", left: "68%" },
  "3B": { top: "56%", left: "18%" },
  "1B": { top: "56%", left: "82%" },
  C: { top: "75%", left: "50%" },
  DH: { top: "82%", left: "80%" },
};

export const staticSpots = [
  {
    label: "P",
    top: "48%",
    left: "50%",
  },
];

