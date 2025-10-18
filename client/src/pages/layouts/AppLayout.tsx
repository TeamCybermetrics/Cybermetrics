import { Outlet } from "react-router-dom";
import { ProtectedRoute, Sidebar, UserBadge } from "@/components";
import styles from "./AppLayout.module.css";

export default function AppLayout() {
  return (
    <div className={styles.shell}>
      <Sidebar />

      <div className={styles.main}>
        <header className={styles.header}>
          <div>
            <p className={styles.heading}>Overview</p>
            <span className={styles.subheading}>Track your roster and scouting insights.</span>
          </div>
          <UserBadge />
        </header>

        <div className={styles.content}>
          <ProtectedRoute>
            <Outlet />
          </ProtectedRoute>
        </div>
      </div>
    </div>
  );
}
