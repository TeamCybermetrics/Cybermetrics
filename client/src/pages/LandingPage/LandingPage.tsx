import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authActions } from "@/actions/auth";
import { Spinner, Footer } from "@/components";
import { ROUTES } from "@/config";
import styles from "./LandingPage.module.css";
import logo from "@/assets/logo_bubble.svg";
import demoImage from "@/assets/demo.png";
import connector from "@/assets/svg/landingPageConnector.svg"; 

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
      <img src={logo} alt="Cybermetrics logo" className={styles.brandLogo} />
      <div className={styles.brandName}>Cybermetrics</div>

      <div className={styles.signUpButtonContainer}>
        {isAuthenticated ? (
          <Link to={ROUTES.TEAM_BUILDER} className={styles.signUpButton}>
            Dashboard
          </Link>
        ) : (
          <>
            <Link to={ROUTES.LOGIN} className={styles.signUpButtonSecondary}>
              Log In
            </Link>
            <Link to={ROUTES.SIGNUP} className={styles.signUpButton}>
              Sign Up
            </Link>
          </>
        )}
      </div>

      <div className={styles.page}>
        <section className={styles.hero}>
          <h2 className={styles.heroTitle}>
            One Dashboard to Manage
            <br />
            Your Baseball team
          </h2>
        </section>

        <section className={styles.demoSection}>
          <div className={styles.demoScreen}>
            <img src={demoImage} alt="Cybermetrics Dashboard Demo" className={styles.demoImage} />
          </div>
        </section>

        <section className={styles.howSection}>
          <h1 className={styles.heading1}>How does it work?</h1>
          <p className={styles.subtitle}>
            an interactive roster-building platform that reimagines how baseball teams evaluate players and construct lineups.
          </p>
          
          <div className={styles.featuresWrap}>
            <div className={styles.featuresRow}>
              <div className={styles.featureCard}>
                <div className={styles.whiteTextBold}>Discover & analyze your team strengths</div>
                <div className={styles.whiteTextRegular}>Find strengths within your team out of 5 key statistics: AVG, OBP, SLG, K%, wRC+</div>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.whiteTextBold}>Identify weaknesses</div>
                <div className={styles.whiteTextRegular}>Use the replacement score to spot holes in your roster.</div>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.whiteTextBold}>Improve with recommendations</div>
                <div className={styles.whiteTextRegular}>Discover and test alternative players within your budget.</div>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.whiteTextBold}>Track competition</div>
                <div className={styles.whiteTextRegular}>Monitor teams targeting similar undervalued players.</div>
              </div>
            </div>

            <img src={connector} alt="" className={styles.connectorSvg} /> {/* Re-add this line */}
          </div>
        </section>
      </div>

      <Footer />
    </main>
  );
}