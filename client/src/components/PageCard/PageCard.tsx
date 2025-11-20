import { ReactNode } from "react";
import styles from "./PageCard.module.css";

interface PageCardProps {
  title: string;
  children: ReactNode;
  className?: string;
  headerAction?: ReactNode;
}

/**
 * Render a styled page card with a header and content area.
 *
 * The header displays the provided title and optionally renders a header action element
 * (e.g., buttons or controls). The children are rendered as the card's content.
 *
 * @param title - The page title displayed in the header
 * @param children - The content to render inside the card
 * @param className - Optional additional CSS class names applied to the outer container
 * @param headerAction - Optional element rendered in the header (for actions or controls)
 * @returns The rendered page card element
 */
export function PageCard({ title, children, className = "", headerAction }: PageCardProps) {
  return (
    <div className={`${styles.page} ${className}`}>
      <header className={styles.header}>
        <div className={styles.kicker}>{title}</div>
        {headerAction && <div className={styles.headerAction}>{headerAction}</div>}
      </header>
      {children}
    </div>
  );
}