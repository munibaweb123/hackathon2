/** Authentication-related TypeScript types for the Todo Web Application */

export interface User {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  name?: string;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
  lastLoginAt?: string;
}

export interface UserRegistrationRequest {
  email: string;
  password: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  name?: string;
}

export interface UserRegistrationResponse {
  success: boolean;
  user: User;
  message?: string;
  accessToken?: string;
  refreshToken?: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserLoginResponse {
  success: boolean;
  user: User;
  accessToken: string;
  refreshToken: string;
  tokenType?: string;
}

export interface TokenRefreshRequest {
  refreshToken: string;
}

export interface TokenRefreshResponse {
  accessToken: string;
  refreshToken: string;
  tokenType?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetResponse {
  success: boolean;
  message: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  newPassword: string;
}

export interface UserProfileUpdateRequest {
  firstName?: string;
  lastName?: string;
  username?: string;
}

export interface UserProfileResponse {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuthErrorResponse {
  success: boolean;
  error: {
    code?: string;
    message: string;
    details?: string;
  };
}

export interface LogoutResponse {
  success: boolean;
  message: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface BetterAuthClient {
  signIn: (provider: string, options?: any) => Promise<any>;
  signOut: () => Promise<void>;
  getSession: () => Promise<any>;
  useSession: () => { data: any; isLoading: boolean };
}