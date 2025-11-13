import { useState, FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { ROUTES } from "@/config";
import logo from "@/assets/brand_badge.jpg";
import styles from "./LoginPage.module.css";

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
        navigate(ROUTES.TEAM_BUILDER);
      }, 1000);
    } else {
      setError(result.error || "An error occurred");
    }

    setIsLoading(false);
  };

  return (
    <div className={styles.page}>
      <div className={styles.stripeBottom}></div>
      
      <div className={styles.logo}>
        <img src={logo} alt="Cybermetrics" />
        <span>Cybermetrics</span>
      </div>

      <div className={styles.container}>
        <h1 className={styles.title}>Login</h1>
        <p className={styles.subtitle}>Welcome back to Cybermetrics</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
              autoComplete="email"
            />
          </div>

          <div className={styles.field}>
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              autoComplete="current-password"
            />
          </div>

          {error && <div className={styles.error} role="alert" aria-live="polite">{error}</div>}
          {success && <div className={styles.success} role="alert" aria-live="polite">{success}</div>}

          <button type="submit" className={styles.submitBtn} disabled={isLoading}>
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className={styles.footer}>
          Don't have an account? <Link to={ROUTES.SIGNUP}>Sign up</Link>
        </p>
      </div>
    </div>
  );
}