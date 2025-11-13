import { authApi } from "@/api/auth";

export const authActions = {
  login: async (email: string, password: string) => {
    try {
      console.log("Attempting login with:", email); // Debug
      const response = await authApi.login({ email, password });
      
      console.log("Login response:", response); // Debug
      
      // Store auth data
      localStorage.setItem("auth_token", response.token);
      localStorage.setItem("user_id", response.user_id);
      localStorage.setItem("user_email", response.email);

      return { success: true, data: response };
    } catch (error) {
      console.error("Login error details:", error); // Debug
      return {
        success: false,
        error: error instanceof Error ? error.message : "Login failed",
      };
    }
  },

  signup: async (email: string, password: string, displayName?: string) => {
    try {
      console.log("Attempting signup with:", email, displayName); // Debug
      const response = await authApi.signup({
        email,
        password,
        display_name: displayName || null,
      });
      
      console.log("Signup response:", response); // Debug

      return { success: true, data: response };
    } catch (error) {
      console.error("Signup error details:", error); // Debug
      return {
        success: false,
        error: error instanceof Error ? error.message : "Signup failed",
      };
    }
  },
  
  logout: () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    return { success: true };
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem("auth_token");
  },

  verifyAuth: async (): Promise<boolean> => {
    const token = localStorage.getItem("auth_token");
    
    if (!token) {
      return false;
    }

    try {
      await authApi.verifyToken();
      return true;
    } catch (error) {
      // Token is invalid or expired, clear it
      authActions.logout();
      return false;
    }
  },

  getCurrentUser: () => {
    return {
      token: localStorage.getItem("auth_token"),
      userId: localStorage.getItem("user_id"),
      email: localStorage.getItem("user_email"),
    };
  },
};

