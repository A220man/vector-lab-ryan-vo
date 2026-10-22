/// <reference types="vite/client" />

import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiError } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        const message = error.response?.data?.detail || error.message;
        return Promise.reject(new Error(message));
      }
    );
  }

  // Health
  async healthCheck() {
    return this.client.get('/health');
  }

  // Documents
  async listDocuments(skip = 0, limit = 50) {
    return this.client.get('/documents', { params: { skip, limit } });
  }

  async getDocument(id: number) {
    return this.client.get(`/documents/${id}`);
  }

  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.client.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async indexDocument(id: number) {
    return this.client.post(`/documents/${id}/index`);
  }

  async incrementalUpdateDocument(id: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.client.post(`/documents/${id}/incremental-update`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async getDocumentVersions(id: number) {
    return this.client.get(`/documents/${id}/versions`);
  }

  // Index
  async getIndexTree(id: number) {
    return this.client.get(`/index/${id}/tree`);
  }

  async getIndexLeaves(id: number) {
    return this.client.get(`/index/${id}/leaves`);
  }

  async searchIndex(id: number, query: string, limit = 10) {
    return this.client.get(`/index/${id}/search`, { params: { q: query, limit } });
  }

  async getNodeDetail(docId: number, nodeId: string) {
    return this.client.get(`/index/${docId}/nodes/${nodeId}`);
  }

  // Chat
  async chat(request: {
    message: string;
    document_id?: number;
    session_id?: number;
    model?: string;
  }) {
    return this.client.post('/chat', request);
  }

  async listSessions(documentId?: number, skip = 0, limit = 20) {
    return this.client.get('/chat/sessions', { params: { document_id: documentId, skip, limit } });
  }

  async getSession(sessionId: number) {
    return this.client.get(`/chat/sessions/${sessionId}`);
  }
}

export const api = new ApiClient();