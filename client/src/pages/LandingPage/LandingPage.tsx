import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { Spinner } from "@/components";
import { ROUTES } from "@/config";
import styles from "./LandingPage.module.css";

export default function LandingPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const isAuth = await authActions.verifyAuth();
      setIsAuthenticated(isAuth);
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return <Spinner />;
  }

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>Cybermetrics</h1>
        <p className={styles.description}>Welcome to the Cybermetrics platform</p>
        <div className={styles.buttons}>
          {isAuthenticated ? (
            <Link to={ROUTES.DASHBOARD} className={styles.button}>
              Dashboard
            </Link>
          ) : (
            <>
              <Link to={ROUTES.LOGIN} className={styles.button}>
                Login
              </Link>
              <Link to={ROUTES.SIGNUP} className={styles.buttonSecondary}>
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
