// Authentication API service for backend integration
import apiClient from './apiClient';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string; // Optional since backend doesn't provide it yet
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    organizationId?: string;
  };
}

export interface UserProfile {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string; // Added to match backend
  is_active?: boolean;
  is_admin?: boolean; 
  is_verified?: boolean; // Added to match backend
  role?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  last_login_at?: string | null;
  // Add other fields that might come from backend
  bio?: string;
  avatar_url?: string;
  // For compatibility with login response
  name?: string;
  organizationId?: string | null;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface PasswordChange {
  old_password: string;
  new_password: string;
}

export interface ProfileUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
}

class AuthApiService {
  private readonly basePath = '/auth';
  
  // Authentication
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    return apiClient.post(`${this.basePath}/login/json`, credentials);
  }
  
  async register(userData: RegisterRequest): Promise<UserProfile> {
    return apiClient.post(`${this.basePath}/register`, userData);
  }
  
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    return apiClient.post(`${this.basePath}/refresh`, { 
      refresh_token: refreshToken 
    });
  }
  
  async logout(): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/logout`);
  }
  
  // User profile
  async getCurrentUser(): Promise<UserProfile> {
    return apiClient.get(`${this.basePath}/me`);
  }
  
  async updateProfile(profileData: ProfileUpdate): Promise<UserProfile> {
    return apiClient.put(`${this.basePath}/me`, profileData);
  }
  
  // Password management
  async changePassword(passwordData: PasswordChange): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/change-password`, passwordData);
  }
  
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/password-reset`, { email });
  }
  
  async confirmPasswordReset(resetData: PasswordResetConfirm): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/password-reset/confirm`, resetData);
  }
  
  // Token management utilities
  setTokens(tokens: AuthResponse): void {
    localStorage.setItem('access_token', tokens.access_token);
    if (tokens.refresh_token) {
      localStorage.setItem('refresh_token', tokens.refresh_token);
    }
    
    // Set a default expiration of 15 minutes (matching backend settings)
    // Backend typically provides 15-minute access tokens
    const expiresIn = 15 * 60; // 15 minutes default
    const expirationTime = Date.now() + (expiresIn * 1000);
    localStorage.setItem('token_expires', expirationTime.toString());
    
    // Store user data
    localStorage.setItem('user_data', JSON.stringify(tokens.user));
    
    console.log(`Token set, expires at: ${new Date(expirationTime).toLocaleTimeString()}`);
  }
  
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }
  
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }
  
  getUserData(): AuthResponse['user'] | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }
  
  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires');
    localStorage.removeItem('user_data');
  }
  
  isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem('token_expires');
    if (!expiresAt) return true;
    
    // Consider expired 2 minutes before actual expiry for safety margin
    const expirationTime = parseInt(expiresAt);
    const timeUntilExpiry = expirationTime - Date.now();
    const isExpiring = timeUntilExpiry <= (2 * 60 * 1000); // 2 minutes
    
    if (isExpiring) {
      console.log(`Token expiring in ${Math.floor(timeUntilExpiry / 1000)}s`);
    }
    
    return isExpiring;
  }
  
  // New method: Get time until token expires
  getTokenExpiryTime(): number | null {
    const expiresAt = localStorage.getItem('token_expires');
    if (!expiresAt) return null;
    
    return parseInt(expiresAt);
  }
  
  // New method: Check if token expires within specified minutes
  isTokenExpiringWithin(minutes: number): boolean {
    const expiryTime = this.getTokenExpiryTime();
    if (!expiryTime) return true;
    
    const timeUntilExpiry = expiryTime - Date.now();
    return timeUntilExpiry <= (minutes * 60 * 1000);
  }
  
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    return !!token && !this.isTokenExpired();
  }
}

export const authApi = new AuthApiService();
export default authApi;