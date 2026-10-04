import { apiClient, apiClientWithMeta, type ApiPaginatedResult } from "@/lib/api-client";
import type {
  OrganizationItem,
  OrganizationDetail,
  OrganizationMember,
  CreateOrganizationPayload,
  UpdateOrganizationPayload,
  AddOrganizationMemberPayload,
  UpdateMemberRolePayload,
} from "@/types/organization";

export const organizationsApi = {
  /**
   * GET /api/v1/organizations
   * List research labs user belongs to
   */
  async listOrganizations(
    params: { page?: number; per_page?: number } = {}
  ): Promise<ApiPaginatedResult<OrganizationItem>> {
    const query = new URLSearchParams();
    if (params.page) query.set("page", params.page.toString());
    if (params.per_page) query.set("per_page", params.per_page.toString());
    const qs = query.toString();
    const endpoint = `/organizations${qs ? `?${qs}` : ""}`;

    return apiClientWithMeta<OrganizationItem>(endpoint, { method: "GET" });
  },

  /**
   * POST /api/v1/organizations
   * Create a new research lab/team
   */
  async createOrganization(payload: CreateOrganizationPayload): Promise<OrganizationItem> {
    return apiClient<OrganizationItem>("/organizations", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * GET /api/v1/organizations/{id}
   * Get lab detail with member roster
   */
  async getOrganization(id: string): Promise<OrganizationDetail> {
    return apiClient<OrganizationDetail>(`/organizations/${id}`, { method: "GET" });
  },

  /**
   * PATCH /api/v1/organizations/{id}
   * Update lab settings or resource quotas
   */
  async updateOrganization(
    id: string,
    payload: UpdateOrganizationPayload
  ): Promise<OrganizationItem> {
    return apiClient<OrganizationItem>(`/organizations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * POST /api/v1/organizations/{id}/members
   * Add a new collaborator to the lab
   */
  async addMember(
    id: string,
    payload: AddOrganizationMemberPayload
  ): Promise<OrganizationMember> {
    return apiClient<OrganizationMember>(`/organizations/${id}/members`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * PATCH /api/v1/organizations/{id}/members/{user_id}
   * Change a collaborator's role in the lab
   */
  async updateMemberRole(
    id: string,
    userId: string,
    payload: UpdateMemberRolePayload
  ): Promise<OrganizationMember> {
    return apiClient<OrganizationMember>(`/organizations/${id}/members/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * DELETE /api/v1/organizations/{id}/members/{user_id}
   * Remove a collaborator from the lab
   */
  async removeMember(id: string, userId: string): Promise<void> {
    return apiClient<void>(`/organizations/${id}/members/${userId}`, {
      method: "DELETE",
    });
  },
};
