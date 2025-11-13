import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { ROUTES } from "@/config";
import logo from "@/assets/brand_badge.jpg";
import styles from "./SignupPage.module.css";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setIsLoading(true);
  setError("");
  setSuccess("");

  const result = await authActions.signup(email, password, displayName);

  if (result.success) {
    setSuccess("Account created successfully! Logging you in...");
    
    // Auto-login after successful signup
    const loginResult = await authActions.login(email, password);
    
    if (loginResult.success) {
      setTimeout(() => {
        navigate(ROUTES.TEAM_BUILDER); // Go straight to app, not login page
      }, 1000);
    } else {
      // If auto-login fails, redirect to login
      setTimeout(() => {
        navigate(ROUTES.LOGIN);
      }, 2000);
    }
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
        <h1 className={styles.title}>Sign Up</h1>
        <p className={styles.subtitle}>Create your Cybermetrics account</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label>Display Name (optional)</label>
            <input
              type="text"
              placeholder="John Doe"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className={styles.field}>
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
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
              minLength={6}
              disabled={isLoading}
            />
          </div>

          {error && <div className={styles.error}>{error}</div>}
          {success && <div className={styles.success}>{success}</div>}

          <button type="submit" className={styles.submitBtn} disabled={isLoading}>
            {isLoading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <p className={styles.footer}>
          Already have an account? <a href={ROUTES.LOGIN}>Log in</a>
        </p>
      </div>
    </div>
  );
}