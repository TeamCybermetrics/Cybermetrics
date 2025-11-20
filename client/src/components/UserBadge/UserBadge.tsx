import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { ROUTES } from "@/config";
import styles from "./UserBadge.module.css";

export default function UserBadge() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  
  const { email } = authActions.getCurrentUser();
  const storedDisplayName = localStorage.getItem("user_display_name");
  const displayName = storedDisplayName || email?.split("@")[0] || "Guest";
  const initials = displayName.charAt(0)?.toUpperCase() || "?";
  const showEmail = !storedDisplayName; // Only show email if no display name

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleLogout = () => {
    authActions.logout();
    navigate(ROUTES.LANDING);
  };

  return (
    <div className={styles.container} ref={dropdownRef}>
      <div className={`${styles.slideContainer} ${isOpen ? styles.slideContainerOpen : ""}`}>
        <button 
          className={styles.badge}
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
        >
          <div className={styles.avatar}>{initials}</div>
          <div className={styles.info}>
            <span className={styles.name}>{displayName}</span>
            {showEmail && email && <span className={styles.meta}>{email}</span>}
          </div>
        </button>

        <button 
          className={styles.logoutButton}
          onClick={handleLogout}
          aria-label="Log out"
        >
          <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
            <path 
              d="M6 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V3.33333C2 2.97971 2.14048 2.64057 2.39052 2.39052C2.64057 2.14048 2.97971 2 3.33333 2H6M10.6667 11.3333L14 8M14 8L10.6667 4.66667M14 8H6" 
              stroke="currentColor" 
              strokeWidth="1.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
