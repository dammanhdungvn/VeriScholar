import { apiClient } from "@/lib/api-client";
import type {
  LoginCredentials,
  RegisterPayload,
  AuthResponse,
  UserProfile,
  AuthTokens,
} from "@/types/auth";
import { mockLogin, mockRegister } from "../data/mock-auth";

interface BackendUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  token_quota?: number;
  tokens_used?: number;
  storage_quota_bytes?: number;
  storage_used_bytes?: number;
  created_at: string;
}

export interface QuotaStatusResponse {
  tokens_used: number;
  token_quota: number;
  tokens_remaining: number;
  storage_used_bytes: number;
  storage_quota_bytes: number;
  percent_token_used: number;
}

interface BackendTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: BackendUser;
}

function mapBackendUser(u: BackendUser): UserProfile {
  return {
    id: u.id,
    email: u.email,
    full_name: u.full_name || u.email.split("@")[0],
    role: (u.role as UserProfile["role"]) || "researcher",
    is_verified: u.is_active,
    token_quota: u.token_quota,
    tokens_used: u.tokens_used,
    storage_quota_bytes: u.storage_quota_bytes,
    storage_used_bytes: u.storage_used_bytes,
    created_at: u.created_at,
  };
}

export const authApi = {
  /**
   * POST /api/v1/auth/login
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    if (import.meta.env.VITE_ENABLE_MOCK_AUTH === "true") {
      return mockLogin(credentials);
    }

    try {
      const res = await apiClient<BackendTokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      });

      const user = mapBackendUser(res.user);
      const tokens: AuthTokens = {
        access_token: res.access_token,
        refresh_token: res.refresh_token,
        token_type: "bearer",
        expires_in: res.expires_in,
      };

      return { user, tokens };
    } catch (err) {
      // In development, fallback to mock if backend server is not yet booted
      if (import.meta.env.DEV && !import.meta.env.VITE_API_BASE_URL) {
        return mockLogin(credentials);
      }
      throw err;
    }
  },

  /**
   * POST /api/v1/auth/register
   */
  async register(payload: RegisterPayload): Promise<AuthResponse> {
    if (import.meta.env.VITE_ENABLE_MOCK_AUTH === "true") {
      return mockRegister(payload);
    }

    try {
      await apiClient<BackendUser>("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: payload.email,
          password: payload.password,
          full_name: payload.full_name,
          role: "researcher",
        }),
      });

      // After registration, authenticate immediately to get tokens
      return await this.login({
        email: payload.email,
        password: payload.password,
        remember_me: true,
      });
    } catch (err) {
      if (import.meta.env.DEV && !import.meta.env.VITE_API_BASE_URL) {
        return mockRegister(payload);
      }
      throw err;
    }
  },

  /**
   * POST /api/v1/auth/refresh
   */
  async refresh(refreshToken: string): Promise<AuthTokens> {
    const res = await apiClient<BackendTokenResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    return {
      access_token: res.access_token,
      refresh_token: res.refresh_token,
      token_type: "bearer",
      expires_in: res.expires_in,
    };
  },

  /**
   * GET /api/v1/auth/me
   */
  async getMe(): Promise<UserProfile> {
    const res = await apiClient<BackendUser>("/auth/me", { method: "GET" });
    return mapBackendUser(res);
  },

  /**
   * POST /api/v1/auth/google
   */
  async loginWithGoogle(idToken: string): Promise<AuthResponse> {
    const res = await apiClient<BackendTokenResponse>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
    });

    const user = mapBackendUser(res.user);
    const tokens: AuthTokens = {
      access_token: res.access_token,
      refresh_token: res.refresh_token,
      token_type: "bearer",
      expires_in: res.expires_in,
    };

    return { user, tokens };
  },

  /**
   * GET /api/v1/auth/quota
   */
  async getQuota(): Promise<QuotaStatusResponse> {
    return await apiClient<QuotaStatusResponse>("/auth/quota", { method: "GET" });
  },
};
