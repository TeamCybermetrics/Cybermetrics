import { NavLink } from "react-router-dom";
import { Hammer, Binoculars, HelpCircle } from "lucide-react";
import { ROUTES } from "@/config";
import logo from "@/assets/brand_badge.jpg";
import UserBadge from "../UserBadge/UserBadge";
import styles from "./Sidebar.module.css";

const analysisItems = [
  { label: "Lineup Constructor", to: ROUTES.LINEUP_CONSTRUCTOR, icon: Hammer },
  { label: "Roster Constructor", to: ROUTES.ROSTER_CONSTRUCTOR, icon: Binoculars },
] as const;

const aboutItems = [
  { label: "About Cybermetrics", to: ROUTES.OUR_ALGORITHM, icon: HelpCircle },
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
                <Icon className={styles.icon} size={20} />
                <span className={styles.label}>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className={styles.sectionHeader}>About</div>
          <nav className={styles.nav}>
            {aboutItems.map(({ label, to, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  [styles.item, isActive ? styles.itemActive : ""].filter(Boolean).join(" ")
                }
              >
                <Icon className={styles.icon} size={20} />
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
