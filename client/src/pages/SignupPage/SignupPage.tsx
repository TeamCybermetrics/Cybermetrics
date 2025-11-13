import { useState } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "@/config";
import logo from "@/assets/brand_badge.jpg";
import styles from "./SignupPage.module.css";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    // auth logic here
  }

  return (
    <div className={styles.page}>
      <div className={styles.stripeBottom}></div> {/* Third stripe */}
      
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
              disabled={loading}
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
            {loading ? "Creating..." : "Login"}
          </button>
        </form>

        <p className={styles.footer}>
          Already have an account? <Link to={ROUTES.LOGIN}>Log in</Link>
        </p>
      </div>
    </div>
  );
}