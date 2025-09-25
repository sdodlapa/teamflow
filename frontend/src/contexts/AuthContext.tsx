import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authApi, UserProfile, AuthResponse } from '../services/authApi';
import { toast } from 'react-hot-toast';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && authApi.isAuthenticated();

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      if (authApi.isAuthenticated()) {
        const userData = await authApi.getCurrentUser();
        setUser(userData);
      } else {
        // Try to refresh token if we have a refresh token
        const refreshToken = authApi.getRefreshToken();
        if (refreshToken) {
          try {
            const tokens = await authApi.refreshToken(refreshToken);
            authApi.setTokens(tokens);
            const userData = await authApi.getCurrentUser();
            setUser(userData);
          } catch (error) {
            // Refresh failed, clear tokens
            authApi.clearTokens();
            setUser(null);
          }
        }
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
      authApi.clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string): Promise<void> => {
    try {
      setIsLoading(true);
      const tokens: AuthResponse = await authApi.login({ username, password });
      authApi.setTokens(tokens);
      
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      
      toast.success('Login successful!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }): Promise<void> => {
    try {
      setIsLoading(true);
      await authApi.register(userData);
      
      // Auto-login after successful registration
      await login(userData.username, userData.password);
      
      toast.success('Registration successful! Welcome to TeamFlow!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authApi.logout();
    } catch (error) {
      // Even if logout fails on backend, clear local state
      console.error('Logout error:', error);
    } finally {
      authApi.clearTokens();
      setUser(null);
      toast.success('Logged out successfully');
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      if (authApi.isAuthenticated()) {
        const userData = await authApi.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};