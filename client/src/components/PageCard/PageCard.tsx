import { ReactNode } from "react";
import styles from "./PageCard.module.css";

interface PageCardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

/**
 * A large page card component with consistent styling across the application.
 * Features a title header with uppercase kicker styling and a content area.
 *
 * @param title - The page title displayed at the top
 * @param children - The content to display within the card
 * @param className - Optional additional CSS class names
 */
export function PageCard({ title, children, className = "" }: PageCardProps) {
  return (
    <div className={`${styles.page} ${className}`}>
      <header className={styles.header}>
        <div className={styles.kicker}>{title}</div>
      </header>
      {children}
    </div>
  );
}
