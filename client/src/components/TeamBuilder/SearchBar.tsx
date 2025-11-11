import { ReactNode } from "react";
import styles from "./SearchBar.module.css";

type SearchBarProps = {
  searchTerm: string;
  onSearchTermChange: (value: string) => void;
  statusText: string;
  errorMessage?: string;
  actions?: ReactNode;
};

export function SearchBar({
  searchTerm,
  onSearchTermChange,
  statusText,
  errorMessage,
  actions,
}: SearchBarProps) {
  return (
    <>
      <div className={styles.searchBar}>
        <span className={styles.searchIcon}>🔍</span>
        <input
          type="text"
          placeholder="Search players by name, team, or position…"
          value={searchTerm}
          onChange={(event) => onSearchTermChange(event.target.value)}
        />
      </div>

      <div className={styles.searchStatus}>{statusText}</div>

      {errorMessage && <p className={styles.playerError}>{errorMessage}</p>}

      {actions}
    </>
  );
}

