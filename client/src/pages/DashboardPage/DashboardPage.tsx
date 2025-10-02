"use client";

import { useEffect, useState } from "react";
import Button from "@/components/Button";
import Alert from "@/components/Alert";
import ProtectedRoute from "@/components/ProtectedRoute";
import { authActions } from "@/actions/auth";
import { healthActions } from "@/actions/health";
import styles from "./DashboardPage.module.css";

export default function DashboardPage() {
  const [userEmail, setUserEmail] = useState("");
  const [healthStatus, setHealthStatus] = useState("");
  const [healthError, setHealthError] = useState("");
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);

  useEffect(() => {
    const user = authActions.getCurrentUser();
    if (user.email) {
      setUserEmail(user.email);
    }
  }, []);

  const handleLogout = () => {
    authActions.logout();
    window.location.href = "/login";
  };

  const handleCheckHealth = async () => {
    setIsCheckingHealth(true);
    setHealthStatus("");
    setHealthError("");

    const result = await healthActions.checkHealth();

    if (result.success) {
      const status = result.data.status;
      const firebaseStatus = result.data.firebase_connected ? "connected" : "disconnected";
      setHealthStatus(`Server is ${status}, Firebase is ${firebaseStatus}`);
    }
    
    if (!result.success) {
      setHealthError(result.error);
    }

    setIsCheckingHealth(false);
  };

  return (
    <ProtectedRoute requireAuth={true}>
      <div className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>Dashboard</h1>
          {userEmail && <p className={styles.email}>Logged in as: {userEmail}</p>}

          <div className={styles.buttons}>
            <Button onClick={handleCheckHealth} disabled={isCheckingHealth}>
              {isCheckingHealth ? "Checking..." : "Check Health"}
            </Button>
            <Button onClick={handleLogout} variant="secondary">
              Logout
            </Button>
          </div>

          {healthStatus && <Alert type="success">{healthStatus}</Alert>}
          {healthError && <Alert type="error">{healthError}</Alert>}
        </div>
      </div>
    </ProtectedRoute>
  );
}

