import { apiClient } from "@/lib/api-client";
import type {
  FolderItem,
  FolderTreeItem,
  FolderCreatePayload,
  FolderUpdatePayload,
  FolderDocumentAssignPayload,
} from "../types";

export const foldersApi = {
  /**
   * List all folders belonging to user
   */
  async listFolders(): Promise<FolderItem[]> {
    return apiClient<FolderItem[]>("/folders", { method: "GET" });
  },

  /**
   * Get recursive nested tree structure of folders
   */
  async getFolderTree(): Promise<FolderTreeItem[]> {
    return apiClient<FolderTreeItem[]>("/folders/tree", { method: "GET" });
  },

  /**
   * Get details for single folder
   */
  async getFolder(id: string): Promise<FolderItem> {
    return apiClient<FolderItem>(`/folders/${id}`, { method: "GET" });
  },

  /**
   * Create a new folder
   */
  async createFolder(payload: FolderCreatePayload): Promise<FolderItem> {
    return apiClient<FolderItem>("/folders", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Update folder name, parent, color, or description
   */
  async updateFolder(id: string, payload: FolderUpdatePayload): Promise<FolderItem> {
    return apiClient<FolderItem>(`/folders/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Delete folder safely
   */
  async deleteFolder(id: string): Promise<{ message?: string; [key: string]: unknown }> {
    return apiClient<{ message?: string }>(`/folders/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * Assign documents to folder
   */
  async assignDocuments(
    id: string,
    payload: FolderDocumentAssignPayload
  ): Promise<{ assigned_count?: number; [key: string]: unknown }> {
    return apiClient<{ assigned_count?: number }>(`/folders/${id}/documents`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Remove documents from folder back to root
   */
  async removeDocuments(
    id: string,
    payload: FolderDocumentAssignPayload
  ): Promise<{ removed_count?: number; [key: string]: unknown }> {
    return apiClient<{ removed_count?: number }>(`/folders/${id}/documents`, {
      method: "DELETE",
      body: JSON.stringify(payload),
    });
  },
};
