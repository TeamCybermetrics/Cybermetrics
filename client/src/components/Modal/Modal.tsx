import React from "react";
import styles from "./Modal.module.css";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
};

/**
 * Base modal component that provides overlay backdrop and content container.
 * 
 * The modal handles:
 * - Overlay backdrop with click-to-close
 * - Content wrapper that prevents click propagation
 * - Basic modal structure (overlay + content container)
 * 
 * Content-specific styling should be handled by the children components.
 * 
 * @param isOpen - Whether the modal is visible
 * @param onClose - Callback to close the modal
 * @param children - Content to render inside the modal
 * @param className - Optional additional CSS class for the content container
 * @returns The modal overlay and content container, or null if not open
 */
export function Modal({ isOpen, onClose, children, className }: Props) {
  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div 
        className={`${styles.content} ${className || ""}`}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}

