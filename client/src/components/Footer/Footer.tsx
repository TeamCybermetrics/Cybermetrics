import { Link } from "react-router-dom";
import { ROUTES } from "@/config";
import styles from "./Footer.module.css";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.section}>
          <div className={styles.brand}>
            <span className={styles.brandName}>Cybermetrics</span>
            <p className={styles.tagline}>
              Advanced baseball analytics for smarter team building
            </p>
          </div>
        </div>

        <div className={styles.section}>
          <h3 className={styles.heading}>Product</h3>
          <nav className={styles.links}>
            <Link to={ROUTES.TEAM_BUILDER} className={styles.link}>
              Team Builder
            </Link>
            <Link to={ROUTES.TEAM_ANALYSIS} className={styles.link}>
              Team Analysis
            </Link>
            <Link to={ROUTES.RECOMMENDATIONS} className={styles.link}>
              Recommendations
            </Link>
          </nav>
        </div>

        <div className={styles.section}>
          <h3 className={styles.heading}>Company</h3>
          <nav className={styles.links}>
            <Link to={ROUTES.OUR_ALGORITHM} className={styles.link}>
              Our Algorithm
            </Link>
          </nav>
        </div>
      </div>

      <div className={styles.bottom}>
        <p className={styles.copyright}>
          © {currentYear} Cybermetrics. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
