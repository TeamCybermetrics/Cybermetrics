import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authActions } from './auth';
import { authApi } from '@/api/auth';

// Mock the auth API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    signup: vi.fn(),
    verifyToken: vi.fn(),
  },
}));

describe('authActions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('should successfully login and store auth data', async () => {
      const mockResponse = {
        token: 'test-token',
        user_id: '123',
        email: 'test@example.com',
        display_name: 'Test User',
        message: 'Login successful',
      };

      vi.mocked(authApi.login).mockResolvedValue(mockResponse);

      const result = await authActions.login('test@example.com', 'password123');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockResponse);
      expect(localStorage.getItem('auth_token')).toBe('test-token');
      expect(localStorage.getItem('user_id')).toBe('123');
      expect(localStorage.getItem('user_email')).toBe('test@example.com');
      expect(localStorage.getItem('user_display_name')).toBe('Test User');
    });

    it('should handle login without display_name', async () => {
      const mockResponse = {
        token: 'test-token',
        user_id: '123',
        email: 'test@example.com',
        message: 'Login successful',
      };

      vi.mocked(authApi.login).mockResolvedValue(mockResponse);

      const result = await authActions.login('test@example.com', 'password123');

      expect(result.success).toBe(true);
      expect(localStorage.getItem('user_display_name')).toBeNull();
    });

    it('should handle login failure', async () => {
      const mockError = new Error('Invalid credentials');
      vi.mocked(authApi.login).mockRejectedValue(mockError);

      const result = await authActions.login('test@example.com', 'wrong-password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid credentials');
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(authApi.login).mockRejectedValue('Unknown error');

      const result = await authActions.login('test@example.com', 'password123');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Login failed');
    });
  });

  describe('signup', () => {
    it('should successfully signup with display name', async () => {
      const mockResponse = {
        message: 'Signup successful',
        user_id: '123',
        email: 'test@example.com',
      };

      vi.mocked(authApi.signup).mockResolvedValue(mockResponse);

      const result = await authActions.signup('test@example.com', 'password123', 'Test User');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockResponse);
      expect(localStorage.getItem('user_display_name')).toBe('Test User');
      expect(authApi.signup).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        display_name: 'Test User',
      });
    });

    it('should successfully signup without display name', async () => {
      const mockResponse = {
        message: 'Signup successful',
        user_id: '123',
        email: 'test@example.com',
      };

      vi.mocked(authApi.signup).mockResolvedValue(mockResponse);

      const result = await authActions.signup('test@example.com', 'password123');

      expect(result.success).toBe(true);
      expect(localStorage.getItem('user_display_name')).toBeNull();
      expect(authApi.signup).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        display_name: null,
      });
    });

    it('should handle signup failure', async () => {
      const mockError = new Error('Email already exists');
      vi.mocked(authApi.signup).mockRejectedValue(mockError);

      const result = await authActions.signup('test@example.com', 'password123');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Email already exists');
    });

    it('should handle non-Error exceptions', async () => {
      vi.mocked(authApi.signup).mockRejectedValue('Unknown error');

      const result = await authActions.signup('test@example.com', 'password123');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Signup failed');
    });
  });

  describe('logout', () => {
    it('should clear all auth data from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('user_id', '123');
      localStorage.setItem('user_email', 'test@example.com');
      localStorage.setItem('user_display_name', 'Test User');

      const result = authActions.logout();

      expect(result.success).toBe(true);
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('user_id')).toBeNull();
      expect(localStorage.getItem('user_email')).toBeNull();
      expect(localStorage.getItem('user_display_name')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when auth token exists', () => {
      localStorage.setItem('auth_token', 'test-token');

      expect(authActions.isAuthenticated()).toBe(true);
    });

    it('should return false when auth token does not exist', () => {
      expect(authActions.isAuthenticated()).toBe(false);
    });
  });

  describe('verifyAuth', () => {
    it('should return true when token is valid', async () => {
      localStorage.setItem('auth_token', 'test-token');
      
      const mockResponse = {
        message: 'Token valid',
        user_id: '123',
        email: 'test@example.com',
      };

      vi.mocked(authApi.verifyToken).mockResolvedValue(mockResponse);

      const result = await authActions.verifyAuth();

      expect(result).toBe(true);
      expect(authApi.verifyToken).toHaveBeenCalled();
      expect(localStorage.getItem('auth_token')).toBe('test-token');
    });

    it('should return false when no token exists', async () => {
      const result = await authActions.verifyAuth();

      expect(result).toBe(false);
      expect(authApi.verifyToken).not.toHaveBeenCalled();
    });

    it('should return false and clear auth data when token is invalid', async () => {
      localStorage.setItem('auth_token', 'invalid-token');
      localStorage.setItem('user_id', '123');
      localStorage.setItem('user_email', 'test@example.com');

      vi.mocked(authApi.verifyToken).mockRejectedValue(new Error('Invalid token'));

      const result = await authActions.verifyAuth();

      expect(result).toBe(false);
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('user_id')).toBeNull();
      expect(localStorage.getItem('user_email')).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user data from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('user_id', '123');
      localStorage.setItem('user_email', 'test@example.com');

      const user = authActions.getCurrentUser();

      expect(user).toEqual({
        token: 'test-token',
        userId: '123',
        email: 'test@example.com',
      });
    });

    it('should return null values when no data exists', () => {
      const user = authActions.getCurrentUser();

      expect(user).toEqual({
        token: null,
        userId: null,
        email: null,
      });
    });
  });
});
