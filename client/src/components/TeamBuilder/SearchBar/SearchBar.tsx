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

/**
 * Render a search input for filtering players with optional status text, error message, and additional actions.
 *
 * @param searchTerm - Current value of the search input.
 * @param onSearchTermChange - Callback invoked with the new input value when the user types.
 * @param statusText - Text shown when a non-empty search term is present.
 * @param errorMessage - Optional error message to display below the search input.
 * @param actions - Optional React nodes rendered after the status and error messages.
 * @param onFocus - Optional focus event callback for the input.
 * @param autoFocus - Optional flag to auto-focus the input on mount.
 * @returns A JSX element containing the search input, conditional status text, conditional error message, and any additional actions.
 */
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
