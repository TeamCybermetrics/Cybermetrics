import { Link as RouterLink } from 'react-router-dom';
import styles from './Link.module.css';

interface LinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
}

export default function Link({ href, children, className }: LinkProps) {
  return (
    <RouterLink to={href} className={className ? `${styles.link} ${className}` : styles.link}>
      {children}
    </RouterLink>
  );
}

