export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'ENGINEER' | 'VIEWER' | 'MANAGER';
  department_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  department_id?: string;
  status: 'ACTIVE' | 'ARCHIVED' | 'SUSPENDED';
  created_at: string;
  updated_at: string;
  document_count: number;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  checksum_sha256: string;
  status: 'UPLOADED' | 'QUEUED' | 'PROCESSING' | 'PARTIALLY_PROCESSED' | 'COMPLETED' | 'FAILED' | 'AWAITING_REVIEW';
  version: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Page {
  id: string;
  page_number: number;
  width?: number;
  height?: number;
  text_content?: string;
  has_images: boolean;
  has_tables: boolean;
  render_path?: string;
  ocr_confidence?: number;
}

export interface EngineeringEntity {
  id: string;
  entity_type: string;
  label?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
  detection_model?: string;
  page_number?: number;
  attributes?: Record<string, any>;
}

export interface SymbolCatalogEntry {
  id: string;
  sno: number;
  name: string;
  function: string;
  description: string;
  category: string;
  criticality: string;
  image_path?: string;
  page_ref?: number;
}

export interface ValidationRule {
  id: string;
  name: string;
  description: string;
  source_standard?: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  is_active: boolean;
}

export interface ValidationResult {
  id: string;
  rule_name: string;
  status: 'PASS' | 'FAIL' | 'REVIEW_REQUIRED' | 'NOT_APPLICABLE' | 'INSUFFICIENT_EVIDENCE';
  severity: string;
  expected_value?: string;
  observed_value?: string;
  evidence?: string;
  entity_id?: string;
  reviewed_by?: string;
  review_notes?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SourceCitation[];
  confidence?: number;
}

export interface SourceCitation {
  document_id: string;
  document_name: string;
  page_number?: number;
  chunk_text?: string;
  relevance_score: number;
}

export interface ComparisonDiff {
  entity_type: string;
  label?: string;
  change_type: 'ADDED' | 'REMOVED' | 'MODIFIED';
  details?: Record<string, any>;
}

export interface ComparisonResponse {
  drawing_a_id: string;
  drawing_b_id: string;
  additions: ComparisonDiff[];
  removals: ComparisonDiff[];
  modifications: ComparisonDiff[];
  summary: string;
}
