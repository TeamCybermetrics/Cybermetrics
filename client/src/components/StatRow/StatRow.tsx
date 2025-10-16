interface StatRowProps {
  label: string;
  value: string | number;
  suffix?: string;
}

export default function StatRow({ label, value, suffix = "" }: StatRowProps) {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      padding: '4px 0', 
      fontSize: '13px' 
    }}>
      <span style={{ color: '#666' }}>{label}:</span>{' '}
      <strong style={{ color: '#000', fontWeight: 'bold' }}>{value}{suffix}</strong>
    </div>
  );
}
