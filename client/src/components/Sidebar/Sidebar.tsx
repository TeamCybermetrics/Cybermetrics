import { NavLink } from "react-router-dom";
import { ROUTES } from "@/config";
import {
  TeamBuilderIcon,
  TeamAnalysisIcon,
} from "@/assets/icons";
import logo from "@/assets/brand_badge.jpg";
import UserBadge from "../UserBadge/UserBadge";
import styles from "./Sidebar.module.css";

const analysisItems = [
  { label: "Team Builder", to: ROUTES.TEAM_BUILDER, icon: TeamBuilderIcon },
  { label: "Team Analysis", to: ROUTES.TEAM_ANALYSIS, icon: TeamAnalysisIcon },
  { label: "Recommendations", to: ROUTES.RECOMMENDATIONS, icon: TeamAnalysisIcon },
] as const;

const aboutItems = [
  { label: "Our Algorithm", to: ROUTES.OUR_ALGORITHM, icon: null },
] as const;

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <img src={logo} alt="Cybermetrics logo" className={styles.logo} />
        <span className={styles.title}>Cybermetrics</span>
      </div>

      <div className={styles.navContainer}>
        <div>
          <div className={styles.sectionHeader}>Analysis</div>
          <nav className={styles.nav}>
            {analysisItems.map(({ label, to, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  [styles.item, isActive ? styles.itemActive : ""].filter(Boolean).join(" ")
                }
              >
                <Icon className={styles.icon} />
                <span className={styles.label}>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className={styles.sectionHeader}>About</div>
          <nav className={styles.nav}>
            {aboutItems.map(({ label, to }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  [styles.item, isActive ? styles.itemActive : ""].filter(Boolean).join(" ")
                }
              >
                <span className={styles.helpIcon}>?</span>
                <span className={styles.label}>{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <div className={styles.userBadgeContainer}>
          <UserBadge />
        </div>
      </div>
    </aside>
  );
}
