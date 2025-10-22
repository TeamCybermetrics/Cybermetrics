import styles from "./StatRow.module.css";

interface StatRowProps {
  label: string;
  value: string | number;
  suffix?: string;
}

export default function StatRow({ label, value, suffix = "" }: StatRowProps) {
  return (
    <div className={styles.row}>
      <span className={styles.label}>{label}</span>
      <strong className={styles.value}>
        {value}
        {suffix}
      </strong>
    </div>
  );
}
