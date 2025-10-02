import styles from './Alert.module.css';

interface AlertProps {
  type: 'error' | 'success';
  children: React.ReactNode;
}

export default function Alert({ type, children }: AlertProps) {
  return (
    <div className={type === 'error' ? styles.error : styles.success}>
      {children}
    </div>
  );
}

