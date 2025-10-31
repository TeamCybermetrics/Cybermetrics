import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { Spinner } from "@/components";
import { ROUTES } from "@/config";
import styles from "./LandingPage.module.css";
import logo from "@/assets/logo_bubble.svg";

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
      {/* Top-left brand on first band */}
      <img src={logo} alt="Cybermetrics logo" className={styles.brandLogo} />
      <div className={styles.brandName}>Cybermetrics</div>

      {/* Hero title */}
      <h2 className={styles.heroTitle}>
        One Dashboard to Manage
        <br />
        Your baseball team
      </h2>
      
      <h3 className={styles.subtitle1}>
       quick description about Cybermetrics here
      </h3>

      {/* Top right Sign Up button */}
    <div className={styles.signUpButtonContainer}>
      {isAuthenticated ? (
        <Link to={ROUTES.DASHBOARD} className={styles.signUpButton}>
          Dashboard
        </Link>
      ) : (
        <>
          <Link to={ROUTES.LOGIN} className={styles.signUpButton}>
            Login
          </Link>
          <Link to={ROUTES.SIGNUP} className={styles.signUpButtonSecondary}>
            Sign Up
          </Link>
        </>
      )}
    </div>
      
      {/* input your MLB team bar */}
      <input 
        type="text" 
        placeholder="Input your MLB team..." 
        className={styles.inputYourTeam}
      />

      {/* Test our demo button */}
      <Link to={ROUTES.SIGNUP} className={styles.TestOurDemoButton}>
        Test our demo
      </Link>

      {/*Demo Screen */}
      <div className={styles.demoScreen}></div>

      {/* How does it work section*/}
      <div className={styles.howSection}>
        <h1 className={styles.heading1}>How does it work?</h1>
        <p className={styles.subtitle}>
          an interactive roster-building platform that reimagines how baseball teams evaluate players and construct lineups.
        </p>

        <div className={styles.featuresRow}>
          <div className={styles.featureCard}>
            <div className={styles.whiteTextBold}>Discover & analyze your team strengths</div>
            <div className={styles.whiteTextRegular}>
              Find strengths within your team out of 5 key statstics: AVG, OBP, SLG, K%, wRC+
            </div>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.whiteTextBold}>2. Identify weaknesses with key metrics</div>
            <div className={styles.whiteTextRegular}>
              Based on an overall replacement score - identify holes in your team
            </div>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.whiteTextBold}>3. Improve with our recommendation System</div>
            <div className={styles.whiteTextRegular}>
              Discover, browse, & test alternative players within your $ range to fill gaps with your team
            </div>
          </div>
          <div className={styles.featureCard}>
            <div className={styles.whiteTextBold}>4. Identify potential threats</div>
            <div className={styles.whiteTextRegular}>
              Track teams with overlapping weaknesses who may target similar undervalued players.
            </div>
          </div>
        </div>

        {/* connector line under the cards */}
        <svg
          className={styles.connectorSvg}
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 1920 284"
          fill="none"
          preserveAspectRatio="none"
        >
          <path
            opacity="0.2"
            d="M-223 139.166H439.366C439.366 139.166 439.366 259.026 439.366 271.23C439.366 283.434 452.863 282.998 452.863 282.998H795.294C795.294 282.998 808.791 283.434 808.791 271.23C808.791 259.026 808.791 23.0215 808.791 12.7681C808.791 1 822.288 1 822.288 1H1113.73C1113.73 1 1126.73 1 1126.73 12.3322C1126.73 22.2084 1126.73 259.026 1126.73 271.23C1126.73 283.434 1140.22 282.998 1140.22 282.998H1474.16C1474.16 282.998 1487.65 283.434 1487.65 271.23C1487.65 259.026 1487.65 139.166 1487.65 139.166H2244"
            stroke="#1E2746"
            strokeWidth="2"
          />
        </svg>
      </div>

    </main>
  );
}
