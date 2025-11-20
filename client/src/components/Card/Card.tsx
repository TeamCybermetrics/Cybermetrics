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
 * Standardized card component with consistent header styling.
 * 
 * @param title - Optional card title (uses heading3 typography)
 * @param subtitle - Optional card subtitle (uses bodySmall typography with muted color)
 * @param children - Card content
 * @param className - Optional additional CSS classes
 * @param variant - Card size variant: "default" or "compact"
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
