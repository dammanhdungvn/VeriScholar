/**
 * VeriScholar Authentication Domain Types
 * Strict 1-1 mapping with Backend FastAPI OpenAPI Schema
 */

export type UserRole = "researcher" | "faculty" | "postdoc" | "student" | "guest";

export interface UserProfile {
  id: string; // UUID v4
  email: string;
  full_name: string;
  institution?: string;
  department?: string;
  academic_rank?: string;
  orcid_id?: string;
  avatar_url?: string;
  bio?: string;
  research_interests?: string;
  google_scholar_url?: string;
  role: UserRole;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number; // Token lifetime in seconds (e.g. 3600)
}

export interface AuthResponse {
  user: UserProfile;
  tokens: AuthTokens;
  message?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  confirm_password?: string;
  institution?: string;
  orcid_id?: string;
  accept_terms: boolean;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export interface UpdateProfilePayload {
  full_name?: string;
  institution?: string;
  department?: string;
  academic_rank?: string;
  orcid_id?: string;
  avatar_url?: string;
  bio?: string;
  research_interests?: string;
  google_scholar_url?: string;
}

export interface AuthMessageResponse {
  message: string;
}

export interface AuthErrorDetail {
  field: string;
  issue: string;
}

export interface AuthErrorResponse {
  code: string;
  message: string;
  detail?: AuthErrorDetail[];
}

export interface VerifyEmailPayload {
  email: string;
  code?: string;
  otp?: string;
  token?: string;
}

export interface ResendVerificationPayload {
  email: string;
}

export interface GoogleLoginPayload {
  id_token: string;
}

