/**
 * Global API Envelope Contracts matching FastAPI Backend OpenAPI Specs
 * Zero 'any' policy strictly enforced.
 */

export interface ApiMeta {
  request_id: string;
  timestamp: string;
}

export interface SingleResponse<T> {
  success: true;
  data: T;
  meta: ApiMeta;
}

export interface PaginationLinks {
  first: string;
  prev: string | null;
  self: string;
  next: string | null;
  last: string;
}

export interface PaginatedMeta extends ApiMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  success: true;
  data: {
    items: T[];
  };
  meta: PaginatedMeta;
  links: PaginationLinks;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  field?: string | null;
  action?: string | null;
}

export interface ErrorResponse {
  success: false;
  error: ApiErrorDetail;
  meta: ApiMeta;
}

/**
 * Immutable Retrieval Unit: BoundingBox Coordinate
 * Normalized floats: [0.0, 1.0] relative to page dimensions
 * Origin (0,0) is Top-Left (Standard for PDF rendering & Web Canvas)
 * Form: [x0, y0, x1, y1, page] where page is strictly 1-indexed (page >= 1)
 */
export type BoundingBox = [number, number, number, number, number];

export interface PageDimensions {
  width_pt: number;
  height_pt: number;
}
