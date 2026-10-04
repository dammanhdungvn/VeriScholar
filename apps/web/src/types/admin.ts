/**
 * Admin Console & System Metrics Domain Types (BỔ SUNG 2)
 */

export interface AdminDashboardMetrics {
  total_users: number;
  active_users: number;
  total_documents: number;
  total_storage_bytes: number;
  total_storage_formatted: string;
  total_tokens_consumed: number;
  total_cost_estimated_usd: number;
  active_sessions: number;
  total_labs: number;
  system_status: string;
}

export interface AdminUserListItem {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "researcher" | "member";
  is_active: boolean;
  token_quota: number;
  tokens_used: number;
  storage_quota_bytes: number;
  storage_used_bytes: number;
  created_at: string;
}

export interface AdminUpdateUserQuotaPayload {
  token_quota?: number;
  storage_quota_bytes?: number;
  role?: "admin" | "researcher" | "member";
  is_active?: boolean;
}

export interface AdminUsageLogItem {
  id: string;
  user_id: string;
  user_email: string;
  activity_type: string;
  model_name?: string;
  tokens_prompt: number;
  tokens_completion: number;
  total_tokens: number;
  cost_cents: number;
  bytes_transferred: number;
  created_at: string;
}

export interface AdminSystemHealth {
  database_connected: boolean;
  storage_dir_healthy: boolean;
  storage_free_bytes: number;
  total_storage_blobs: number;
  average_latency_ms: number;
}
