import NextLink from 'next/link';
import styles from './Link.module.css';

interface LinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
}

export default function Link({ href, children, className }: LinkProps) {
  return (
    <NextLink href={href} className={className ? `${styles.link} ${className}` : styles.link}>
      {children}
    </NextLink>
  );
}

