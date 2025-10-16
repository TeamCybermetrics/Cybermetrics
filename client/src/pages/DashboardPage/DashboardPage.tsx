import { useEffect, useState, useCallback } from "react";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Alert from "@/components/Alert";
import PlayerCard from "@/components/PlayerCard";
import ProtectedRoute from "@/components/ProtectedRoute";
import { authActions } from "@/actions/auth";
import { healthActions } from "@/actions/health";
import { playerActions } from "@/actions/players";
import { PlayerSearchResult, SavedPlayer } from "@/api/players";
import styles from "./DashboardPage.module.css";

export default function DashboardPage() {
  const [userEmail, setUserEmail] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PlayerSearchResult[]>([]);
  const [savedPlayers, setSavedPlayers] = useState<SavedPlayer[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [healthStatus, setHealthStatus] = useState("");
  const [healthError, setHealthError] = useState("");
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);

  useEffect(() => {
    const user = authActions.getCurrentUser();
    if (user.email) {
      setUserEmail(user.email);
    }
    loadSavedPlayers();
  }, []);

  const loadSavedPlayers = async () => {
    const result = await playerActions.getSavedPlayers();
    if (result.success && result.data) {
      setSavedPlayers(result.data);
    }
  };

  const performSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    setError("");
    const result = await playerActions.searchPlayers(query);
    setIsSearching(false);

    if (result.success && result.data) {
      setSearchResults(result.data);
    } else {
      setError(result.error || "Search failed");
      setSearchResults([]);
    }
  }, []);

  // Debounce search while typing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      performSearch(searchQuery);
    }, 300); // 300ms delay after user stops typing

    return () => clearTimeout(timeoutId);
  }, [searchQuery, performSearch]);

  const handleAddPlayer = async (player: PlayerSearchResult) => {
    setError("");
    setSuccess("");
    
    const result = await playerActions.addPlayer({ 
      id: player.id, 
      name: player.name,
      image_url: player.image_url,
      years_active: player.years_active
    });

    if (result.success) {
      setSuccess(`Added ${player.name} to saved players`);
      await loadSavedPlayers();
      setTimeout(() => setSuccess(""), 3000);
    } else {
      setError(result.error || "Failed to add player");
    }
  };

  const handleDeletePlayer = async (playerId: number, playerName: string) => {
    setError("");
    setSuccess("");
    
    const result = await playerActions.deletePlayer(playerId);

    if (result.success) {
      setSuccess(`Removed ${playerName} from saved players`);
      await loadSavedPlayers();
      setTimeout(() => setSuccess(""), 3000);
    } else {
      setError(result.error || "Failed to remove player");
    }
  };

  const handleLogout = () => {
    authActions.logout();
    window.location.href = "/login";
  };

  const handleCheckHealth = async () => {
    setIsCheckingHealth(true);
    setHealthStatus("");
    setHealthError("");

    const result = await healthActions.checkHealth();

    if (result.success) {
      const status = result.data.status;
      const firebaseStatus = result.data.firebase_connected ? "connected" : "disconnected";
      setHealthStatus(`Server is ${status}, Firebase is ${firebaseStatus}`);
    }
    
    if (!result.success) {
      setHealthError(result.error);
    }

    setIsCheckingHealth(false);
  };

  return (
    <ProtectedRoute requireAuth={true}>
      <div className={styles.container}>
        <div className={styles.content}>
          <div className={styles.header}>
            <h1 className={styles.title}>Dashboard</h1>
            {userEmail && <p className={styles.email}>Logged in as: {userEmail}</p>}
          </div>

          {/* Search Section */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>Search Players</h2>
            <div className={styles.searchBox}>
              <Input
                type="text"
                placeholder="Start typing to search for a player..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {isSearching && <span className={styles.searchingIndicator}>Searching...</span>}
            </div>

            {searchResults.length > 0 && (
              <div className={styles.resultsList}>
                {searchResults.map((player) => (
                  <div key={player.id} className={styles.resultItem}>
                    <div 
                      className={styles.playerClickable}
                      onClick={() => setSelectedPlayerId(player.id)}
                    >
                      <img 
                        src={player.image_url} 
                        alt={player.name}
                        className={styles.playerImage}
                        onError={(e) => {
                          e.currentTarget.src = 'https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current';
                        }}
                      />
                      <div className={styles.playerInfo}>
                        <span className={styles.playerName}>{player.name}</span>
                        <span className={styles.playerMeta}>{player.years_active}</span>
                        <span className={styles.playerId}>ID: {player.id}</span>
                      </div>
                    </div>
                    <Button 
                      onClick={() => handleAddPlayer(player)}
                      variant="secondary"
                    >
                      Add
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {searchQuery && !isSearching && searchResults.length === 0 && (
              <p className={styles.emptyMessage}>No players found matching "{searchQuery}"</p>
            )}
          </div>

          {/* Saved Players Section */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>Saved Players</h2>
            {savedPlayers.length === 0 ? (
              <p className={styles.emptyMessage}>No saved players yet. Search and add some!</p>
            ) : (
              <div className={styles.savedList}>
                {savedPlayers.map((player) => (
                  <div key={player.id} className={styles.savedItem}>
                    <div 
                      className={styles.playerClickable}
                      onClick={() => setSelectedPlayerId(player.id)}
                    >
                      <img 
                        src={player.image_url || 'https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current'} 
                        alt={player.name}
                        className={styles.playerImage}
                        onError={(e) => {
                          e.currentTarget.src = 'https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/0/headshot/67/current';
                        }}
                      />
                      <div className={styles.playerInfo}>
                        <span className={styles.playerName}>{player.name}</span>
                        {player.years_active && <span className={styles.playerMeta}>{player.years_active}</span>}
                        <span className={styles.playerId}>ID: {player.id}</span>
                      </div>
                    </div>
                    <Button 
                      onClick={() => handleDeletePlayer(player.id, player.name)}
                      variant="secondary"
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Alerts */}
          {success && <Alert type="success">{success}</Alert>}
          {error && <Alert type="error">{error}</Alert>}

          {/* Bottom Actions */}
          <div className={styles.bottomActions}>
            <Button onClick={handleCheckHealth} disabled={isCheckingHealth} variant="secondary">
              {isCheckingHealth ? "Checking..." : "Check Health"}
            </Button>
            <Button onClick={handleLogout} variant="secondary">
              Logout
            </Button>
          </div>

          {healthStatus && <Alert type="success">{healthStatus}</Alert>}
          {healthError && <Alert type="error">{healthError}</Alert>}
        </div>

        {selectedPlayerId && (
          <PlayerCard
            playerId={selectedPlayerId}
            onClose={() => setSelectedPlayerId(null)}
          />
        )}
      </div>
    </ProtectedRoute>
  );
}
