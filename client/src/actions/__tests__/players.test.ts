import { describe, it, expect, vi, beforeEach } from 'vitest';
import { playerActions } from '../players';
import { playersApi } from '@/api/players';

// Mock the players API
vi.mock('@/api/players', () => ({
  playersApi: {
    search: vi.fn(),
    getDetail: vi.fn(),
    getSaved: vi.fn(),
    addSaved: vi.fn(),
    deleteSaved: vi.fn(),
    updateSavedPosition: vi.fn(),
    getTeamWeakness: vi.fn(),
    getPlayerValueScores: vi.fn(),
    getRecommendations: vi.fn(),
  },
}));

describe('playerActions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('searchPlayers', () => {
    it('should successfully search for players', async () => {
      const mockResults = [
        {
          id: 1,
          name: 'Mike Trout',
          score: 95.5,
          image_url: 'https://example.com/trout.jpg',
          years_active: '2011-2024',
        },
        {
          id: 2,
          name: 'Shohei Ohtani',
          score: 98.2,
          image_url: 'https://example.com/ohtani.jpg',
          years_active: '2018-2024',
        },
      ];

      vi.mocked(playersApi.search).mockResolvedValue(mockResults);

      const result = await playerActions.searchPlayers('trout');

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResults);
      }
      expect(playersApi.search).toHaveBeenCalledWith('trout', undefined);
    });

    it('should handle search with abort signal', async () => {
      const mockResults = [
        {
          id: 1,
          name: 'Mike Trout',
          score: 95.5,
          image_url: 'https://example.com/trout.jpg',
          years_active: '2011-2024',
        },
      ];

      const abortController = new AbortController();
      vi.mocked(playersApi.search).mockResolvedValue(mockResults);

      const result = await playerActions.searchPlayers('trout', abortController.signal);

      expect(result.success).toBe(true);
      expect(playersApi.search).toHaveBeenCalledWith('trout', abortController.signal);
    });

    it('should handle cancelled requests', async () => {
      const abortError = new Error('Request cancelled');
      abortError.name = 'AbortError';
      vi.mocked(playersApi.search).mockRejectedValue(abortError);

      const result = await playerActions.searchPlayers('trout');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Request cancelled');
        expect(result.aborted).toBe(true);
      }
    });

    it('should handle search failure', async () => {
      const mockError = new Error('Network error');
      vi.mocked(playersApi.search).mockRejectedValue(mockError);

      const result = await playerActions.searchPlayers('trout');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Network error');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.search).mockRejectedValue('Unknown error');

      const result = await playerActions.searchPlayers('trout');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Search failed');
      }
    });
  });

  describe('getPlayerDetail', () => {
    it('should successfully get player details', async () => {
      const mockDetail = {
        mlbam_id: 545361,
        fangraphs_id: 19755,
        name: 'Mike Trout',
        image_url: 'https://example.com/trout.jpg',
        years_active: '2011-2024',
        team_abbrev: 'LAA',
        overall_score: 95.5,
        seasons: {
          '2023': {
            games: 82,
            plate_appearances: 350,
            at_bats: 300,
            hits: 90,
            singles: 50,
            doubles: 20,
            triples: 2,
            home_runs: 18,
            runs: 50,
            rbi: 44,
            walks: 45,
            strikeouts: 75,
            stolen_bases: 5,
            caught_stealing: 2,
            batting_average: 0.300,
            on_base_percentage: 0.400,
            slugging_percentage: 0.550,
            ops: 0.950,
            isolated_power: 0.250,
            babip: 0.320,
            walk_rate: 0.129,
            strikeout_rate: 0.214,
            bb_k_ratio: 0.600,
            woba: 0.380,
            wrc_plus: 150,
            war: 5.5,
            off: 30.5,
            def_: -2.5,
            base_running: 1.0,
          },
        },
      };

      vi.mocked(playersApi.getDetail).mockResolvedValue(mockDetail);

      const result = await playerActions.getPlayerDetail(545361);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockDetail);
      }
      expect(playersApi.getDetail).toHaveBeenCalledWith(545361);
    });

    it('should handle get player detail failure', async () => {
      const mockError = new Error('Player not found');
      vi.mocked(playersApi.getDetail).mockRejectedValue(mockError);

      const result = await playerActions.getPlayerDetail(999999);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Player not found');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.getDetail).mockRejectedValue('Unknown error');

      const result = await playerActions.getPlayerDetail(545361);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to fetch player details');
      }
    });
  });

  describe('getSavedPlayers', () => {
    it('should successfully get saved players', async () => {
      const mockPlayers = [
        {
          id: 1,
          name: 'Mike Trout',
          image_url: 'https://example.com/trout.jpg',
          years_active: '2011-2024',
          position: 'CF',
        },
        {
          id: 2,
          name: 'Shohei Ohtani',
          image_url: 'https://example.com/ohtani.jpg',
          years_active: '2018-2024',
          position: 'DH',
        },
      ];

      vi.mocked(playersApi.getSaved).mockResolvedValue(mockPlayers);

      const result = await playerActions.getSavedPlayers();

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockPlayers);
      }
      expect(playersApi.getSaved).toHaveBeenCalled();
    });

    it('should handle get saved players failure', async () => {
      const mockError = new Error('Unauthorized');
      vi.mocked(playersApi.getSaved).mockRejectedValue(mockError);

      const result = await playerActions.getSavedPlayers();

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Unauthorized');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.getSaved).mockRejectedValue('Unknown error');

      const result = await playerActions.getSavedPlayers();

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to fetch saved players');
      }
    });
  });

  describe('addPlayer', () => {
    it('should successfully add a player', async () => {
      const playerToAdd = {
        id: 1,
        name: 'Mike Trout',
        image_url: 'https://example.com/trout.jpg',
        years_active: '2011-2024',
      };

      const mockResponse = {
        message: 'Player added successfully',
        player_id: '1',
      };

      vi.mocked(playersApi.addSaved).mockResolvedValue(mockResponse);

      const result = await playerActions.addPlayer(playerToAdd);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResponse);
      }
      expect(playersApi.addSaved).toHaveBeenCalledWith(playerToAdd);
    });

    it('should handle add player failure', async () => {
      const playerToAdd = {
        id: 1,
        name: 'Mike Trout',
      };

      const mockError = new Error('Player already exists');
      vi.mocked(playersApi.addSaved).mockRejectedValue(mockError);

      const result = await playerActions.addPlayer(playerToAdd);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Player already exists');
      }
    });

    it('should handle non-Error exceptions', async () => {
      const playerToAdd = {
        id: 1,
        name: 'Mike Trout',
      };

      vi.mocked(playersApi.addSaved).mockRejectedValue('Unknown error');

      const result = await playerActions.addPlayer(playerToAdd);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to add player');
      }
    });
  });

  describe('deletePlayer', () => {
    it('should successfully delete a player', async () => {
      const mockResponse = {
        message: 'Player deleted successfully',
      };

      vi.mocked(playersApi.deleteSaved).mockResolvedValue(mockResponse);

      const result = await playerActions.deletePlayer(1);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResponse);
      }
      expect(playersApi.deleteSaved).toHaveBeenCalledWith(1);
    });

    it('should handle delete player failure', async () => {
      const mockError = new Error('Player not found');
      vi.mocked(playersApi.deleteSaved).mockRejectedValue(mockError);

      const result = await playerActions.deletePlayer(999);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Player not found');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.deleteSaved).mockRejectedValue('Unknown error');

      const result = await playerActions.deletePlayer(1);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to delete player');
      }
    });
  });

  describe('updatePlayerPosition', () => {
    it('should successfully update player position', async () => {
      const mockPlayer = {
        id: 1,
        name: 'Mike Trout',
        image_url: 'https://example.com/trout.jpg',
        years_active: '2011-2024',
        position: 'CF',
      };

      vi.mocked(playersApi.updateSavedPosition).mockResolvedValue(mockPlayer);

      const result = await playerActions.updatePlayerPosition(1, 'CF');

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockPlayer);
      }
      expect(playersApi.updateSavedPosition).toHaveBeenCalledWith(1, 'CF');
    });

    it('should successfully update player position to null', async () => {
      const mockPlayer = {
        id: 1,
        name: 'Mike Trout',
        image_url: 'https://example.com/trout.jpg',
        years_active: '2011-2024',
        position: null,
      };

      vi.mocked(playersApi.updateSavedPosition).mockResolvedValue(mockPlayer);

      const result = await playerActions.updatePlayerPosition(1, null);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockPlayer);
      }
      expect(playersApi.updateSavedPosition).toHaveBeenCalledWith(1, null);
    });

    it('should handle update player position failure', async () => {
      const mockError = new Error('Player not found');
      vi.mocked(playersApi.updateSavedPosition).mockRejectedValue(mockError);

      const result = await playerActions.updatePlayerPosition(999, 'CF');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Player not found');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.updateSavedPosition).mockRejectedValue('Unknown error');

      const result = await playerActions.updatePlayerPosition(1, 'CF');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to update player position');
      }
    });
  });

  describe('getTeamWeakness', () => {
    it('should successfully get team weakness', async () => {
      const mockWeakness = {
        strikeout_rate: 0.25,
        walk_rate: 0.08,
        isolated_power: 0.15,
        on_base_percentage: 0.320,
        base_running: -2.5,
      };

      vi.mocked(playersApi.getTeamWeakness).mockResolvedValue(mockWeakness);

      const result = await playerActions.getTeamWeakness([1, 2, 3]);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockWeakness);
      }
      expect(playersApi.getTeamWeakness).toHaveBeenCalledWith([1, 2, 3]);
    });

    it('should handle get team weakness failure', async () => {
      const mockError = new Error('Insufficient data');
      vi.mocked(playersApi.getTeamWeakness).mockRejectedValue(mockError);

      const result = await playerActions.getTeamWeakness([1]);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Insufficient data');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.getTeamWeakness).mockRejectedValue('Unknown error');

      const result = await playerActions.getTeamWeakness([1, 2, 3]);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to load team weaknesses');
      }
    });
  });

  describe('getPlayerValueScores', () => {
    it('should successfully get player value scores', async () => {
      const mockScores = [
        {
          id: 1,
          name: 'Mike Trout',
          adjustment_score: 85.5,
          value_score: 92.3,
        },
        {
          id: 2,
          name: 'Shohei Ohtani',
          adjustment_score: 90.2,
          value_score: 95.8,
        },
      ];

      vi.mocked(playersApi.getPlayerValueScores).mockResolvedValue(mockScores);

      const result = await playerActions.getPlayerValueScores([1, 2]);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockScores);
      }
      expect(playersApi.getPlayerValueScores).toHaveBeenCalledWith([1, 2]);
    });

    it('should handle get player value scores failure', async () => {
      const mockError = new Error('Players not found');
      vi.mocked(playersApi.getPlayerValueScores).mockRejectedValue(mockError);

      const result = await playerActions.getPlayerValueScores([999]);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Players not found');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.getPlayerValueScores).mockRejectedValue('Unknown error');

      const result = await playerActions.getPlayerValueScores([1, 2]);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to load player scores');
      }
    });
  });

  describe('getRecommendations', () => {
    it('should successfully get recommendations', async () => {
      const mockRecommendations = [
        {
          id: 3,
          name: 'Aaron Judge',
          score: 96.5,
          image_url: 'https://example.com/judge.jpg',
          years_active: '2016-2024',
        },
        {
          id: 4,
          name: 'Mookie Betts',
          score: 94.8,
          image_url: 'https://example.com/betts.jpg',
          years_active: '2014-2024',
        },
      ];

      vi.mocked(playersApi.getRecommendations).mockResolvedValue(mockRecommendations);

      const result = await playerActions.getRecommendations([1, 2]);

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockRecommendations);
      }
      expect(playersApi.getRecommendations).toHaveBeenCalledWith([1, 2]);
    });

    it('should handle get recommendations failure', async () => {
      const mockError = new Error('Insufficient roster data');
      vi.mocked(playersApi.getRecommendations).mockRejectedValue(mockError);

      const result = await playerActions.getRecommendations([]);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Insufficient roster data');
      }
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(playersApi.getRecommendations).mockRejectedValue('Unknown error');

      const result = await playerActions.getRecommendations([1, 2]);

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Failed to get recommendations');
      }
    });
  });
});
