/**
 * Public Resource Sharing & Instant Revocation Types
 */

export interface CreateSharePayload {
  resource_type: "document" | "note" | "draft" | "collection";
  resource_id: string;
  permission?: "read_only";
  expires_at?: string | null;
}

export interface ShareResponse {
  share_token: string;
  resource_type: string;
  resource_id: string;
  permission: string;
  share_url: string;
  expires_at: string | null;
  created_at: string;
}

export interface PublicShareResource {
  share_token: string;
  resource_type: string;
  resource_id: string;
  permission: string;
  resource_data: Record<string, unknown>;
  created_at: string;
}
