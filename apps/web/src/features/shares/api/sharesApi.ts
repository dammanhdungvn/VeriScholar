import {
  apiClient,
  apiClientBlob,
} from "@/lib/api-client";
import type {
  CreateSharePayload,
  ShareResponse,
  PublicShareResource,
} from "@/types/share";

export const sharesApi = {
  /**
   * POST /api/v1/shares
   * Generate an unguessable cryptographic token for sharing an academic resource
   */
  async createShare(payload: CreateSharePayload): Promise<ShareResponse> {
    return apiClient<ShareResponse>("/shares", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * GET /api/v1/shares/{token}
   * Zero-auth public retrieval of shared resource
   */
  async getPublicShare(token: string): Promise<PublicShareResource> {
    return apiClient<PublicShareResource>(`/shares/${token}`, {
      method: "GET",
    });
  },

  /**
   * GET /api/v1/shares/{token}/file
   * Zero-auth stream of shared PDF file with HTTP 206 support
   */
  async streamSharedFile(token: string): Promise<Blob> {
    return apiClientBlob(`/shares/${token}/file`);
  },

  /**
   * DELETE /api/v1/shares/{token}
   * Instant revocation: immediately turns all future guest requests to HTTP 410 Gone
   */
  async revokeShare(token: string): Promise<void> {
    return apiClient<void>(`/shares/${token}`, {
      method: "DELETE",
    });
  },
};
