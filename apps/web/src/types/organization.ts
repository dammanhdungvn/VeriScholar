/**
 * Collaborative Lab / Organization Domain Types (BỔ SUNG 2)
 */

export interface OrganizationMember {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: "owner" | "admin" | "member" | "guest";
  created_at: string;
}

export interface OrganizationItem {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  storage_quota_bytes: number;
  storage_used_bytes: number;
  token_quota: number;
  tokens_used: number;
  members_count: number;
  user_role: string;
  created_at: string;
}

export interface OrganizationDetail extends OrganizationItem {
  members: OrganizationMember[];
}

export interface CreateOrganizationPayload {
  name: string;
  slug: string;
  description?: string;
}

export interface UpdateOrganizationPayload {
  name?: string;
  description?: string;
  token_quota?: number;
  storage_quota_bytes?: number;
}

export interface AddOrganizationMemberPayload {
  email: string;
  role?: "admin" | "member" | "guest";
}

export interface UpdateMemberRolePayload {
  role: "owner" | "admin" | "member" | "guest";
}
