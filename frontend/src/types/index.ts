export interface Document {
  id: number;
  filename: string;
  status: 'pending' | 'processing' | 'indexed' | 'failed';
  page_count: number;
  version: number;
  content_hash: string;
  parent_id?: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface IndexNode {
  node_id: string;
  structure?: string;
  title: string;
  content?: string;
  summary?: string;
  level: number;
  parent_node_id?: string;
  start_page?: number;
  end_page?: number;
  content_hash?: string;
  summary_hash?: string;
  nodes?: IndexNode[];
}

export interface IndexTree {
  nodes: IndexNode[];
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model?: string;
  usage?: {
    input_tokens?: number;
    output_tokens?: number;
    cache_read_tokens?: number;
    cache_write_tokens?: number;
    reasoning_tokens?: number;
    complete: number;
  };
  created_at: string;
}

export interface ChatSession {
  id: number;
  document_id?: number;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface ChatRequest {
  message: string;
  document_id?: number;
  session_id?: number;
  model?: string;
}

export interface ChatResponse {
  response: string;
  session_id: number;
  usage: {
    input_tokens?: number;
    output_tokens?: number;
    cache_read_tokens?: number;
    cache_write_tokens?: number;
    reasoning_tokens?: number;
    complete: number;
    model?: string;
  };
}

export interface DocumentVersion {
  version: number;
  content_hash: string;
  changed_node_ids: string[];
  change_summary?: string;
  created_at: string;
}

export interface SearchResult {
  node_id: string;
  structure?: string;
  title: string;
  summary?: string;
  level: number;
  match_type: 'title' | 'content' | 'summary';
}

export interface ApiError {
  detail: string;
}