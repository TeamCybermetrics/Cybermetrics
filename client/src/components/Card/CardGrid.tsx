import { ReactNode } from "react";
import styles from "./CardGrid.module.css";

interface CardGridProps {
  children: ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: "small" | "medium" | "large";
  className?: string;
}

/**
 * Render a responsive grid container for card elements.
 *
 * @param children - Content to render inside the grid.
 * @param columns - Number of columns (1–4). Defaults to 2.
 * @param gap - Spacing between cards: "small" (12px), "medium" (20px), or "large" (28px). Defaults to "medium".
 * @param className - Additional CSS class names to append to the grid container.
 * @returns The div element that acts as the grid container and contains the provided children.
 */
export function CardGrid({ children, columns = 2, gap = "medium", className = "" }: CardGridProps) {
  const gridClass = `${styles.grid} ${styles[`grid${columns}Col`]} ${styles[`gap${gap.charAt(0).toUpperCase() + gap.slice(1)}`]} ${className}`;
  
  return (
    <div className={gridClass}>
      {children}
    </div>
  );
}