import styles from './Button.module.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
}

export default function Button({ variant = 'primary', children, className, ...props }: ButtonProps) {
  const buttonClass = variant === 'secondary' 
    ? `${styles.button} ${styles.secondary}` 
    : styles.button;
  
  return (
    <button 
      className={className ? `${buttonClass} ${className}` : buttonClass}
      {...props}
    >
      {children}
    </button>
  );
}

