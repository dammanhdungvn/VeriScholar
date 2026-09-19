import type { BoundingBox, PageDimensions } from "./api";

export interface DemoCitation {
  id: string;
  label: string; // e.g., "Vaswani et al. • Tr. 6"
  paper_title: string;
  page: number;
  bounding_box: BoundingBox;
  quote_text: string;
  fact_check_status: "supported" | "contradicted" | "unverified";
}

export interface DemoTurn {
  id: string;
  user_query: string;
  ai_thought?: string; // Thinking chain (Socratic reasoning)
  ai_answer_markdown: string;
  citations: DemoCitation[];
  presupposition_corrected: boolean; // Socratic prompt presupposition validation
}

export interface DemoPaper {
  id: string;
  title: string;
  authors: string;
  venue_year: string;
  total_pages: number;
  page_dimensions: PageDimensions;
  rotation_deg: 0 | 90 | 180 | 270;
  sample_turns: DemoTurn[];
  mock_page_paragraphs: {
    column: 1 | 2;
    text: string;
    has_formula?: boolean;
    formula_text?: string;
  }[];
}

export interface FeatureMetric {
  metric_value: string;
  metric_label: string;
  description: string;
}

export interface ComparisonRow {
  feature: string;
  description: string;
  verischolar: string | boolean;
  claude: string | boolean;
  perplexity: string | boolean;
  notebooklm: string | boolean;
  chatpdf: string | boolean;
}

export interface WorkflowStep {
  step_number: string;
  title: string;
  description: string;
  badge: string;
}
