"""
Shared pytest fixtures and configuration for all tests.
"""
import pytest
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))


@pytest.fixture
def sample_player_data():
    """Sample player data for testing"""
    return {
        "mlbam_id": 545361,
        "fangraphs_id": 10155,
        "name": "Mike Trout",
        "team_abbrev": "LAA",
        "overall_score": 95.5,
        "seasons": {
            "2023": {
                "games": 150,
                "plate_appearances": 600,
                "at_bats": 550,
                "hits": 180,
                "home_runs": 40,
                "strikeout_rate": 0.200,
                "walk_rate": 0.150,
                "isolated_power": 0.250,
                "on_base_percentage": 0.380,
                "base_running": 2.5,
                "batting_average": 0.327,
                "slugging_percentage": 0.645,
                "ops": 1.025,
                "war": 8.5
            },
            "2022": {
                "games": 119,
                "plate_appearances": 500,
                "at_bats": 450,
                "hits": 150,
                "home_runs": 35,
                "strikeout_rate": 0.190,
                "walk_rate": 0.140,
                "isolated_power": 0.240,
                "on_base_percentage": 0.370,
                "base_running": 2.0,
                "batting_average": 0.333,
                "slugging_percentage": 0.630,
                "ops": 1.000,
                "war": 7.2
            }
        }
    }


@pytest.fixture
def sample_season_stats():
    """Sample season stats for testing"""
    return {
        "games": 150,
        "plate_appearances": 600,
        "at_bats": 550,
        "hits": 180,
        "singles": 100,
        "doubles": 30,
        "triples": 5,
        "home_runs": 45,
        "runs": 110,
        "rbi": 120,
        "walks": 80,
        "strikeouts": 120,
        "stolen_bases": 15,
        "caught_stealing": 3,
        "batting_average": 0.327,
        "on_base_percentage": 0.410,
        "slugging_percentage": 0.645,
        "ops": 1.055,
        "isolated_power": 0.318,
        "babip": 0.310,
        "walk_rate": 0.133,
        "strikeout_rate": 0.200,
        "bb_k_ratio": 0.667,
        "woba": 0.420,
        "wrc_plus": 180,
        "war": 8.5,
        "off": 55.0,
        "def": 5.0,
        "base_running": 2.5,
        "team_abbrev": "LAA"
    }


@pytest.fixture
def sample_player_ids():
    """Sample player IDs for testing"""
    return [545361, 660271, 592450, 502110, 608070]


@pytest.fixture
def test_client():
    """Create FastAPI test client for integration/e2e tests"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_auth_header():
    """Mock authorization header for testing authenticated endpoints"""
    return {"Authorization": "Bearer mock_test_token_12345"}


