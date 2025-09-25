// Authentication API service for backend integration
import apiClient from './apiClient';

export interface LoginRequest {
  username: string;
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
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
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
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return apiClient.post(`${this.basePath}/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
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
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('token_expires', (Date.now() + tokens.expires_in * 1000).toString());
  }
  
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }
  
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }
  
  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires');
  }
  
  isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem('token_expires');
    if (!expiresAt) return true;
    
    return Date.now() > parseInt(expiresAt) - 60000; // Consider expired 1 minute before actual expiry
  }
  
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    return !!token && !this.isTokenExpired();
  }
}

export const authApi = new AuthApiService();
export default authApi;