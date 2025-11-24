import { describe, it, expect, vi, beforeEach } from 'vitest';
import { healthActions } from '../health';
import { healthApi } from '@/api/health';

// Mock the health API
vi.mock('@/api/health', () => ({
  healthApi: {
    check: vi.fn(),
  },
}));

describe('healthActions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('checkHealth', () => {
    it('should successfully check health', async () => {
      const mockResponse = {
        status: 'healthy',
        firebase_connected: true,
      };

      vi.mocked(healthApi.check).mockResolvedValue(mockResponse);

      const result = await healthActions.checkHealth();

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data).toEqual(mockResponse);
      }
      expect(healthApi.check).toHaveBeenCalled();
    });

    it('should handle health check failure with Error', async () => {
      const mockError = new Error('Service unavailable');
      vi.mocked(healthApi.check).mockRejectedValue(mockError);

      const result = await healthActions.checkHealth();

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Service unavailable');
      }
    });

    it('should handle health check failure with non-Error', async () => {
      vi.mocked(healthApi.check).mockRejectedValue('Unknown error');

      const result = await healthActions.checkHealth();

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBe('Health check failed');
      }
    });
  });
});
