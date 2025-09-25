/**
 * Authentication hook for TeamFlow
 */
import { useState, useEffect, useCallback } from 'react';
import apiClient, { ApiError } from '../services/apiClient';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  organizationId?: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

/**
 * Custom hook that handles authentication functionality
 */
export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setIsLoading(false);
        return;
      }
      
      try {
        const userData = await apiClient.get<User>('/auth/me');
        setUser(userData);
        setIsAuthenticated(true);
        setIsLoading(false);
      } catch (error) {
        // Token is invalid or expired
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        setIsAuthenticated(false);
        setUser(null);
        setError('Session expired. Please log in again.');
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login function
  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post<LoginResponse>('/auth/login/json', {
        email,
        password
      });
      
      const { access_token, refresh_token, user: userData } = response;
      
      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Update state
      setUser(userData);
      setIsAuthenticated(true);
      setIsLoading(false);
      
      return true;
    } catch (err) {
      const apiError = err as ApiError;
      const errorMsg = apiError.message || 'Login failed. Please check your credentials.';
      
      setError(errorMsg);
      setIsLoading(false);
      
      return false;
    }
  }, []);

  // Logout function
  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Reset state
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
      setIsLoading(false);
    }
  }, []);

  // Register/signup function
  const signup = useCallback(async (
    name: string, 
    email: string, 
    password: string
  ): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Split the name into first and last name
      const nameParts = name.trim().split(' ');
      const firstName = nameParts[0] || '';
      const lastName = nameParts.slice(1).join(' ') || '';
      
      await apiClient.post('/auth/register', {
        first_name: firstName,
        last_name: lastName,
        email,
        password
      });
      
      // Registration successful but user needs verification
      // Don't auto-login, just show success message
      setIsLoading(false);
      setError('Account created successfully! Please check your email for verification (for demo purposes, you can login immediately).');
      
      return true;
    } catch (err) {
      const apiError = err as ApiError;
      const errorMsg = apiError.message || 'Registration failed. Please try again.';
      
      setError(errorMsg);
      setIsLoading(false);
      
      return false;
    }
  }, []);

  // Reset password function
  const resetPassword = useCallback(async (email: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiClient.post('/auth/password-reset', { email });
      setIsLoading(false);
      return true;
    } catch (err) {
      const apiError = err as ApiError;
      const errorMsg = apiError.message || 'Password reset failed. Please try again.';
      
      setError(errorMsg);
      setIsLoading(false);
      
      return false;
    }
  }, []);

  // Update profile
  const updateProfile = useCallback(async (userData: Partial<User>): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedUser = await apiClient.patch<User>('/users/me', userData);
      setUser(updatedUser);
      setIsLoading(false);
      return true;
    } catch (err) {
      const apiError = err as ApiError;
      const errorMsg = apiError.message || 'Failed to update profile.';
      
      setError(errorMsg);
      setIsLoading(false);
      return false;
    }
  }, []);

  return {
    isAuthenticated,
    isLoading,
    user,
    error,
    login,
    logout,
    signup,
    resetPassword,
    updateProfile
  };
};

export default useAuth;