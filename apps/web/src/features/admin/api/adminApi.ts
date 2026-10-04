import { apiClient, apiClientWithMeta, type ApiPaginatedResult } from "@/lib/api-client";
import type {
  AdminDashboardMetrics,
  AdminUserListItem,
  AdminUpdateUserQuotaPayload,
  AdminUsageLogItem,
  AdminSystemHealth,
} from "@/types/admin";

export const adminApi = {
  /**
   * GET /api/v1/admin/dashboard
   * Real-time metrics on users, storage, and LLM compute
   */
  async getDashboardMetrics(): Promise<AdminDashboardMetrics> {
    return apiClient<AdminDashboardMetrics>("/admin/dashboard", { method: "GET" });
  },

  /**
   * GET /api/v1/admin/users
   * Paginated user list with quota allocations
   */
  async listUsers(
    params: { page?: number; per_page?: number; search?: string } = {}
  ): Promise<ApiPaginatedResult<AdminUserListItem>> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    if (params.search) query.set("search", params.search);
    const qs = query.toString();
    const endpoint = `/admin/users${qs ? `?${qs}` : ""}`;

    return apiClientWithMeta<AdminUserListItem>(endpoint, { method: "GET" });
  },

  /**
   * PATCH /api/v1/admin/users/{id}/quota
   * Adjust user token limit, storage quota, role, or active status
   */
  async updateUserQuota(
    userId: string,
    payload: AdminUpdateUserQuotaPayload
  ): Promise<AdminUserListItem> {
    return apiClient<AdminUserListItem>(`/admin/users/${userId}/quota`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * GET /api/v1/admin/usage
   * Detailed audit trail of LLM and compute consumption
   */
  async listUsageLogs(
    params: { page?: number; per_page?: number; user_id?: string } = {}
  ): Promise<ApiPaginatedResult<AdminUsageLogItem>> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    if (params.user_id) query.set("user_id", params.user_id);
    const qs = query.toString();
    const endpoint = `/admin/usage${qs ? `?${qs}` : ""}`;

    return apiClientWithMeta<AdminUsageLogItem>(endpoint, { method: "GET" });
  },

  /**
   * GET /api/v1/admin/system-health
   * Hardware, CAS storage, and database probe
   */
  async getSystemHealth(): Promise<AdminSystemHealth> {
    return apiClient<AdminSystemHealth>("/admin/system-health", { method: "GET" });
  },
};
