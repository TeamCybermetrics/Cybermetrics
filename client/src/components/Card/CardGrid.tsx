import { ReactNode } from "react";
import styles from "./CardGrid.module.css";

interface CardGridProps {
  children: ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: "small" | "medium" | "large";
  className?: string;
}

/**
 * Grid layout container for cards with responsive behavior.
 * 
 * @param children - Card components to display in grid
 * @param columns - Number of columns (1-4), defaults to 2
 * @param gap - Spacing between cards: "small" (12px), "medium" (20px), or "large" (28px)
 * @param className - Optional additional CSS classes
 */
export function CardGrid({ children, columns = 2, gap = "medium", className = "" }: CardGridProps) {
  const gridClass = `${styles.grid} ${styles[`grid${columns}Col`]} ${styles[`gap${gap.charAt(0).toUpperCase() + gap.slice(1)}`]} ${className}`;
  
  return (
    <div className={gridClass}>
      {children}
    </div>
  );
}
