import styles from "./StrengthView.module.css";

export default function StrengthView() {
  const players = [
    { name: "Keymetric1", change: "+43%", avatar: "https://via.placeholder.com/50" },
    { name: "Keymetric222", change: "+43%", avatar: "https://via.placeholder.com/50" },
    { name: "Keymetric3", change: "+43%", avatar: "https://via.placeholder.com/50" },
    { name: "Keymetric4", change: "+43%", avatar: "https://via.placeholder.com/50" },
    { name: "Kemetriv5", change: "+43%", avatar: "https://via.placeholder.com/50" },
  ];

  return (
    <div className={styles.container}>
      {/* Bubble statistics bar */}
      <div className={styles.statsBubble}>
        <div className={styles.statsHeader}>Statistics</div>
        <div className={styles.statsRow}>
          <div className={styles.statBlock}>
            <div className={styles.statLabel}>Team Score</div>
            <div className={styles.statValueGreen}>+130</div>
          </div>
          <div className={styles.statBlock}>
            <div className={styles.statLabel}>Somedataxxxxxxxx</div>
            <div className={styles.statValue}>Moredataaxxx</div>
          </div>
        </div>
      </div>

      {/* Main content grid */}
      <div className={styles.grid}>
        <div className={styles.leftColumn}>
          <h2 className={styles.sectionTitle}>Your Team's top performance metrics...</h2>
          <div className={styles.playerList}>
            {players.map((p, i) => (
              <div key={i} className={styles.playerCard}>
                <img src={p.avatar} alt={p.name} className={styles.avatar} />
                <span className={styles.playerName}>{p.name}</span>
                <div className={styles.chart}>
                  <svg width="60" height="24" viewBox="0 0 60 24">
                    <polyline points="0,20 15,16 30,12 45,8 60,4" fill="none" stroke="#00ff88" strokeWidth="2" />
                  </svg>
                </div>
                <span className={styles.change}>{p.change}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.radarSection}>
          <div className={styles.radarCard}>
            <div className={styles.radarLabel}>Key strengths</div>
            <div className={styles.radarChart}>
              {/* Responsive radar chart with viewBox */}
              <svg viewBox="0 0 280 280" style={{ maxWidth: '280px', width: '100%', height: 'auto' }}>
                <polygon points="140,30 210,80 210,200 140,250 70,200 70,80" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <polygon points="140,60 190,95 190,185 140,220 90,185 90,95" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <polygon points="140,90 170,110 170,170 140,190 110,170 110,110" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="140" y1="140" x2="140" y2="30" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="140" y1="140" x2="210" y2="80" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="140" y1="140" x2="210" y2="200" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="140" y1="140" x2="140" y2="250" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="140" y1="140" x2="70" y2="200" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <line x1="140" y1="140" x2="70" y2="80" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
                <polygon points="140,50 200,90 200,190 140,215 95,170 95,110" fill="rgba(109,123,255,0.2)" stroke="#6d7bff" strokeWidth="2" />
                <text x="140" y="20" textAnchor="middle" fill="#fff" fontSize="10">Strikeouts</text>
                <text x="225" y="85" textAnchor="start" fill="#fff" fontSize="10">Walk Rate</text>
                <text x="225" y="205" textAnchor="start" fill="#fff" fontSize="10">Isolated Power</text>
                <text x="140" y="270" textAnchor="middle" fill="#fff" fontSize="10">On Base %</text>
                <text x="50" y="205" textAnchor="end" fill="#fff" fontSize="10">Durability</text>
                <text x="50" y="85" textAnchor="end" fill="#fff" fontSize="10">Age</text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}