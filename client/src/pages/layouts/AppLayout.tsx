import { Outlet } from "react-router-dom";
import { ProtectedRoute, Sidebar, UserBadge } from "@/components";
import styles from "./AppLayout.module.css";

export default function AppLayout() {
  return (
    <div className={styles.shell}>
      <Sidebar />

      <div className={styles.main}>
        <div className={styles.topBar}>
          <UserBadge />
        </div>

        <div className={styles.content}>
          <ProtectedRoute>
            <Outlet />
          </ProtectedRoute>
        </div>
      </div>
    </div>
  );
}
