import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { ROUTES } from "@/config";
import styles from "./UserBadge.module.css";

/**
 * Renders a hover-activated user badge showing an avatar, display name, optional email, and a logout control.
 *
 * The badge expands while hovered to reveal a logout button; the logout button is disabled briefly to allow the open animation to finish. The component reads the current user via authActions.getCurrentUser() and prefers a stored display name from localStorage; if no stored name exists it shows the email's local-part and displays the full email as metadata. Activating the logout control calls authActions.logout() and navigates to ROUTES.LANDING.
 *
 * @returns A JSX element containing the user badge with avatar initials, display name, optional email metadata, and a logout button.
 */
export default function UserBadge() {
  const [isOpen, setIsOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const animationTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const navigate = useNavigate();
  
  const { email } = authActions.getCurrentUser();
  const storedDisplayName = localStorage.getItem("user_display_name");
  const displayName = storedDisplayName || email?.split("@")[0] || "Guest";
  const initials = displayName.charAt(0)?.toUpperCase() || "?";
  const showEmail = !storedDisplayName; // Only show email if no display name

  // Cleanup animation timeout on unmount
  useEffect(() => {
    return () => {
      if (animationTimeoutRef.current) {
        clearTimeout(animationTimeoutRef.current);
      }
    };
  }, []);

  const handleMouseEnter = () => {
    if (animationTimeoutRef.current) {
      clearTimeout(animationTimeoutRef.current);
    }
    setIsOpen(true);
    setIsAnimating(true);
    // Animation duration is 0.3s, so wait 300ms before allowing logout
    animationTimeoutRef.current = setTimeout(() => {
      setIsAnimating(false);
    }, 300);
  };

  const handleMouseLeave = () => {
    if (animationTimeoutRef.current) {
      clearTimeout(animationTimeoutRef.current);
    }
    setIsOpen(false);
    setIsAnimating(false);
  };

  const handleLogout = () => {
    authActions.logout();
    navigate(ROUTES.LANDING);
  };

  return (
    <div 
      className={styles.container} 
      ref={dropdownRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className={`${styles.slideContainer} ${isOpen ? styles.slideContainerOpen : ""}`}>
        <div className={styles.badge}>
          <div className={styles.avatar}>{initials}</div>
          <div className={styles.info}>
            <span className={styles.name}>{displayName}</span>
            {showEmail && email && <span className={styles.meta}>{email}</span>}
          </div>
        </div>

        <button 
          className={styles.logoutButton}
          onClick={handleLogout}
          disabled={isAnimating}
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