import { useState } from "react";

export type PanelMode = "idle" | "recommendations" | "search";

export function useRecommendations() {
  const [mode, setMode] = useState<PanelMode>("idle");
  const [query, setQuery] = useState("");

  const onGetRecommendations = () => setMode("recommendations");
  
  const onSearchChange = (value: string) => {
    setQuery(value);
    setMode(value ? "search" : "idle");
  };

  const onSaveLineup = () => {
    // TODO: integrate SaveTeamPopUp
  };

  return { mode, query, onGetRecommendations, onSearchChange, onSaveLineup };
}