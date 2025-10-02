"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { authActions } from "@/actions/auth";
import { Spinner } from "@/components";
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
            <Link href="/dashboard" className={styles.button}>
              Dashboard
            </Link>
          ) : (
            <>
              <Link href="/login" className={styles.button}>
                Login
              </Link>
              <Link href="/signup" className={styles.buttonSecondary}>
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </main>
  );
}

