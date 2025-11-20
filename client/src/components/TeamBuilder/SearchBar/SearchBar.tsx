import { ReactNode } from "react";
import styles from "./SearchBar.module.css";

type SearchBarProps = {
  searchTerm: string;
  onSearchTermChange: (value: string) => void;
  statusText: string;
  errorMessage?: string;
  actions?: ReactNode;
  onFocus?: () => void;
  autoFocus?: boolean;
};

export function SearchBar({
  searchTerm,
  onSearchTermChange,
  statusText,
  errorMessage,
  actions,
  onFocus,
  autoFocus,
}: SearchBarProps) {
  const hasSearchTerm = searchTerm.trim().length > 0;
  
  return (
    <>
      <div className={styles.searchBar}>
        <svg className={styles.searchIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input
          type="text"
          placeholder="Search players by name…"
          value={searchTerm}
          onChange={(event) => onSearchTermChange(event.target.value)}
          onFocus={onFocus}
          autoFocus={autoFocus}
        />
      </div>

      {hasSearchTerm && <div className={styles.searchStatus}>{statusText}</div>}

      {errorMessage && <p className={styles.playerError}>{errorMessage}</p>}

      {actions}
    </>
  );
}

