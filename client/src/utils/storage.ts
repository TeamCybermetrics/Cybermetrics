import { STORAGE_KEYS } from "@/config";

export const storage = {
  setToken: (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    }
  },

  getToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    }
    return null;
  },

  removeToken: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    }
  },

  setUserData: (userId: string, email: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
      localStorage.setItem(STORAGE_KEYS.USER_EMAIL, email);
    }
  },

  getUserData: () => {
    if (typeof window !== 'undefined') {
      return {
        userId: localStorage.getItem(STORAGE_KEYS.USER_ID),
        email: localStorage.getItem(STORAGE_KEYS.USER_EMAIL),
      };
    }
    return { userId: null, email: null };
  },

  clearAll: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_ID);
      localStorage.removeItem(STORAGE_KEYS.USER_EMAIL);
    }
  },
};

