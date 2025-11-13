import { useState } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "@/config";
import logo from "@/assets/brand_badge.jpg";
import styles from "./LoginPage.module.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    // auth logic here
  }

  return (
    <div className={styles.page}>
      <div className={styles.stripeBottom}></div>
      
      <div className={styles.logo}>
        <img src={logo} alt="Cybermetrics" />
        <span>Cybermetrics</span>
      </div>

      <div className={styles.container}>
        <h1 className={styles.title}>Login</h1>
        <p className={styles.subtitle}>Access your Cybermetrics account</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
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
              disabled={loading}
            />
          </div>

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className={styles.footer}>
          Don't have an account? <Link to={ROUTES.SIGNUP}>Sign up</Link>
        </p>
      </div>
    </div>
  );
}