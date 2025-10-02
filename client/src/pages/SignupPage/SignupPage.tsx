"use client";

import { useState, FormEvent } from "react";
import { AuthCard, Input, Button, Alert, Link, ProtectedRoute } from "@/components";
import { authActions } from "@/actions/auth";
import styles from "./SignupPage.module.css";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    const result = await authActions.signup(email, password, displayName);

    if (result.success) {
      setSuccess("Account created successfully! Redirecting to login...");
      setEmail("");
      setPassword("");
      setDisplayName("");

      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
    } else {
      setError(result.error || "An error occurred");
    }

    setIsLoading(false);
  };

  return (
    <ProtectedRoute requireAuth={false}>
      <AuthCard
        title="Sign Up"
        subtitle="Create your Cybermetrics account"
        footer={
          <p>
            Already have an account? <Link href="/login">Login</Link>
          </p>
        }
      >
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input
            label="Display Name (optional)"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="John Doe"
            disabled={isLoading}
          />

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
            minLength={6}
            disabled={isLoading}
            hint="Minimum 6 characters"
          />

          {error && <Alert type="error">{error}</Alert>}
          {success && <Alert type="success">{success}</Alert>}

          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Creating account..." : "Sign Up"}
          </Button>
        </form>
      </AuthCard>
    </ProtectedRoute>
  );
}

