import styles from "./BudgetBreakdownView.module.css";

export default function BudgetBreakdownView() {
  return (
    <div className={styles.container}>
      <div className={styles.budgetHeader}>
        <h1 className={styles.budgetTitle}>Team Budget</h1>
        <div className={styles.budgetAmount}>$153,460,346</div>
      </div>

      <div className={styles.playerCard}>
        <div className={styles.playerInfo}>
          <div className={styles.playerName}>Sdfia Nasdm</div>
          <div className={styles.playerSalary}>$123456</div>
        </div>

        <div className={styles.bars}>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className={styles.bar}>
              <div className={styles.barTop}></div>
              <div className={styles.barBottom}></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}