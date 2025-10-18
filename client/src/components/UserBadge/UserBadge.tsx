import { authActions } from "@/actions/auth";
import styles from "./UserBadge.module.css";

export default function UserBadge() {
  const { email } = authActions.getCurrentUser();
  const displayName = email ? email.split("@")[0] : "Guest";
  const initials = displayName ? displayName.charAt(0).toUpperCase() : "?";

  return (
    <div className={styles.badge}>
      <div className={styles.avatar}>{initials}</div>
      <div className={styles.info}>
        <span className={styles.name}>{displayName}</span>
        {email && <span className={styles.meta}>{email}</span>}
      </div>
    </div>
  );
}
