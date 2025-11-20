import { Outlet } from "react-router-dom";
import { ProtectedRoute, Sidebar, Footer } from "@/components";
import styles from "./AppLayout.module.css";

/**
 * Renders the application shell with navigation, a protected main content area for child routes, and a footer.
 *
 * @returns A JSX element containing a sidebar, a protected content area that renders matching child routes, and a footer.
 */
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