import { apiClient } from "@/lib/api-client";
import { foldersApi } from "./foldersApi";
import type {
  ComparisonMatrixRequest,
  ComparisonMatrixResponse,
  HierarchicalRagRequest,
  HierarchicalRagResponse,
} from "../types";

export const synthesisApi = {
  /**
   * Generate Global Literature Comparison Matrix across whole library or given doc IDs
   */
  async generateComparisonMatrix(
    payload: ComparisonMatrixRequest
  ): Promise<ComparisonMatrixResponse> {
    return foldersApi.generateComparisonMatrix(payload);
  },

  /**
   * Generate Literature Comparison Matrix scoped to specific folder
   */
  async generateFolderComparisonMatrix(
    folderId: string,
    payload: ComparisonMatrixRequest
  ): Promise<ComparisonMatrixResponse> {
    return foldersApi.generateComparisonMatrix({
      ...payload,
      folder_id: folderId,
    });
  },

  /**
   * Execute 2-tier Hierarchical RAG search (Tier 1 Notes -> Tier 2 Chunks)
   * with Sufficiency Gate evaluation across Library or selected folder.
   */
  async hierarchicalRagQuery(
    payload: HierarchicalRagRequest
  ): Promise<HierarchicalRagResponse> {
    return apiClient<HierarchicalRagResponse>("/folders/synthesis", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Execute 2-tier Hierarchical RAG search scoped to specific folder
   */
  async folderHierarchicalRagQuery(
    folderId: string,
    payload: HierarchicalRagRequest
  ): Promise<HierarchicalRagResponse> {
    return apiClient<HierarchicalRagResponse>(`/folders/${folderId}/synthesis`, {
      method: "POST",
      body: JSON.stringify({ ...payload, folder_id: folderId }),
    });
  },
};
