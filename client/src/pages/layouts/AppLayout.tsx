import { Outlet } from "react-router-dom";
import { ProtectedRoute, Sidebar, Footer } from "@/components";
import styles from "./AppLayout.module.css";

export default function AppLayout() {
  return (
    <div className={styles.shell}>
      <Sidebar />

      <div className={styles.main}>
        <div className={styles.content}>
          <ProtectedRoute>
            <Outlet />
          </ProtectedRoute>
        </div>

        <Footer />
      </div>
    </div>
  );
}
