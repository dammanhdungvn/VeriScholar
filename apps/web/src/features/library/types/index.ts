/**
 * Types for Module 4: Personal Paper Library & Folders
 */

export interface FolderItem {
  id: string;
  user_id: string;
  name: string;
  parent_id: string | null;
  color: string;
  description: string | null;
  document_count: number;
  subfolder_count: number;
  created_at: string;
  updated_at: string;
}

export interface FolderTreeItem {
  id: string;
  name: string;
  parent_id: string | null;
  color: string;
  description: string | null;
  document_count: number;
  subfolders: FolderTreeItem[];
}

export interface FolderCreatePayload {
  name: string;
  parent_id?: string | null;
  color?: string;
  description?: string | null;
}

export interface FolderUpdatePayload {
  name?: string;
  parent_id?: string | null;
  color?: string;
  description?: string | null;
}

export interface FolderDocumentAssignPayload {
  document_ids: string[];
}
