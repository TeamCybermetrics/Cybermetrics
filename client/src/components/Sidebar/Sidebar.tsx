import { NavLink, Link } from "react-router-dom";
import { ROUTES } from "@/config";
import {
  TeamBuilderIcon,
  TeamAnalysisIcon,
} from "@/assets/icons";
import logo from "@/assets/brand_badge.jpg";
import styles from "./Sidebar.module.css";

const navItems = [
  { label: "Team Builder", to: ROUTES.TEAM_BUILDER, icon: TeamBuilderIcon },
  { label: "Team Analysis", to: ROUTES.TEAM_ANALYSIS, icon: TeamAnalysisIcon },
  { label: "Recommendations", to: ROUTES.RECOMMENDATIONS, icon: TeamAnalysisIcon }, // add
] as const;

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <img src={logo} alt="Cybermetrics logo" className={styles.logo} />
        <span className={styles.title}>Cybermetrics</span>
      </div>

      <nav className={styles.nav}>
        {navItems.map(({ label, to, icon: Icon }) => (
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

      <Link
        to={ROUTES.OUR_ALGORITHM}
        aria-label="Learn about our algorithm"
        title="Our Algorithm"
        className={styles.helpFab}
      >
        ?
      </Link>
    </aside>
  );
}
