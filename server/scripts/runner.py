import asyncio
from datetime import datetime

from infrastructure.player_repository import PlayerRepositoryFirebase
from infrastructure.roster_repository import RosterRepositoryFirebase  # added concrete impl
from useCaseHelpers.roster_helper import RosterDomain
from config.firebase import firebase_service
from scripts.seed_teams import seed_all_teams
from scripts.get_players import refresh_players
from scripts.get_league_average import main as run_league_average

try:
    from services.roster_avg_service import RosterAvgService
except ImportError:
    RosterAvgService = None

START_YEAR = 2015
CURRENT_SEASON = 2024

def log(msg: str) -> None:
    print(f"[{datetime.utcnow().isoformat()}Z] {msg}")

def run_seed_teams(repo: PlayerRepositoryFirebase) -> None:
    log("Seed teams start")
    try:
        seed_all_teams(repo, CURRENT_SEASON)
        log("Seed teams done")
    except Exception as e:
        log(f"Seed teams failed: {e}")

def run_refresh_players(repo: PlayerRepositoryFirebase) -> None:
    log("Refresh players start")
    try:
        count = refresh_players(repo, start_year=START_YEAR, current_season=CURRENT_SEASON)
        log(f"Refresh players done (upserted {count})")
    except Exception as e:
        log(f"Refresh players failed: {e}")

async def run_league(repo: PlayerRepositoryFirebase) -> None:
    if RosterAvgService is None:
        log("RosterAvgService not available; skipping league averages.")
        return
    log("League averages start")
    try:
        roster_service = RosterAvgService(
            roster_repository=RosterRepositoryFirebase(firebase_service.db),
            roster_domain=RosterDomain(),
            player_repository=repo
        )
        await run_league_average(repo, roster_service)
        log("League averages done")
    except Exception as e:
        log(f"League averages failed: {e}")

async def run_all():
    if not firebase_service.db:
        log("Firebase not configured; aborting.")
        return
    repo = PlayerRepositoryFirebase(firebase_service.db)
    run_seed_teams(repo)
    run_refresh_players(repo)
    await run_league(repo)

def main():
    asyncio.run(run_all())

if __name__ == "__main__":
    main()