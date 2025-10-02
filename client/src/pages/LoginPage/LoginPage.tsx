"use client";

import { useState, FormEvent } from "react";
import { AuthCard, Input, Button, Alert, Link, ProtectedRoute } from "@/components";
import { authActions } from "@/actions/auth";
import styles from "./LoginPage.module.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    const result = await authActions.login(email, password);

    if (result.success) {
      setSuccess("Login successful!");
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 1000);
    } else {
      setError(result.error || "An error occurred");
    }

    setIsLoading(false);
  };

  return (
    <ProtectedRoute requireAuth={false}>
      <AuthCard
        title="Login"
        subtitle="Welcome back to Cybermetrics"
        footer={
          <p>
            Don&apos;t have an account? <Link href="/signup">Sign up</Link>
          </p>
        }
      >
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            disabled={isLoading}
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            disabled={isLoading}
          />

          {error && <Alert type="error">{error}</Alert>}
          {success && <Alert type="success">{success}</Alert>}

          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Logging in..." : "Login"}
          </Button>
        </form>
      </AuthCard>
    </ProtectedRoute>
  );
}

