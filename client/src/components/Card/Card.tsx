import { ReactNode } from "react";
import typography from "@/styles/typography.module.css";
import styles from "./Card.module.css";

interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  variant?: "default" | "compact";
  headerAction?: ReactNode;
}

/**
 * Render a styled card component with an optional header and a content area.
 *
 * The header is rendered only when `title`, `subtitle`, or `headerAction` is provided.
 *
 * @param title - Optional card title shown in the header
 * @param subtitle - Optional card subtitle shown below the title in the header
 * @param children - Content displayed inside the card body
 * @param className - Optional additional CSS classes applied to the card container
 * @param variant - Visual variant of the card; `"compact"` reduces spacing, `"default"` uses standard spacing
 * @param headerAction - Optional node rendered on the right side of the header (e.g., buttons or controls)
 * @returns A JSX element representing the card
 */
export function Card({ title, subtitle, children, className = "", variant = "default", headerAction }: CardProps) {
  return (
    <div className={`${styles.card} ${variant === "compact" ? styles.cardCompact : ""} ${className}`}>
      {(title || subtitle || headerAction) && (
        <div className={styles.header}>
          <div className={styles.headerContent}>
            {title && <div className={typography.heading3}>{title}</div>}
            {subtitle && <div className={`${typography.bodySmall} ${typography.muted}`}>{subtitle}</div>}
          </div>
          {headerAction && <div className={styles.headerAction}>{headerAction}</div>}
        </div>
      )}
      <div className={styles.content}>
        {children}
      </div>
    </div>
  );
}