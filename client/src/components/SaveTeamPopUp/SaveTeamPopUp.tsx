import { useEffect } from "react";
import styles from "./SaveTeamPopUp.module.css";

interface SaveTeamPopUpProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export function SaveTeamPopUp({ isOpen, onClose, children }: SaveTeamPopUpProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}