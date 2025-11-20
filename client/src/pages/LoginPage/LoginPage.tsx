import { useState, FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { ROUTES } from "@/config";
import { AuthCard, Input, Button, Alert } from "@/components";
import logo from "@/assets/brand_badge.jpg";
import styles from "./LoginPage.module.css";

/**
 * Render the login page and handle user authentication.
 *
 * Displays a form for email and password, shows error or success alerts, and disables inputs while submitting.
 * On successful authentication it shows a success message and navigates to ROUTES.LINEUP_CONSTRUCTOR after 1 second.
 *
 * @returns The login page as a JSX element
 */
export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    const result = await authActions.login(email, password);

    if (result.success) {
      setSuccess("Login successful!");
      setTimeout(() => {
        navigate(ROUTES.LINEUP_CONSTRUCTOR);
      }, 1000);
    } else {
      setError(result.error || "An error occurred");
    }

    setIsLoading(false);
  };

  return (
    <div className={styles.page}>
      <div className={styles.logo}>
        <img src={logo} alt="Cybermetrics" />
        <span>Cybermetrics</span>
      </div>

      <AuthCard
        title="Login"
        subtitle="Welcome back to Cybermetrics"
        footer={
          <p>
            Don't have an account? <Link to={ROUTES.SIGNUP}>Sign up</Link>
          </p>
        }
      >
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
            autoComplete="email"
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
            autoComplete="current-password"
          />

          {error && (
            <Alert type="error">
              {error}
            </Alert>
          )}
          {success && (
            <Alert type="success">
              {success}
            </Alert>
          )}

          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Logging in..." : "Login"}
          </Button>
        </form>
      </AuthCard>
    </div>
  );
}