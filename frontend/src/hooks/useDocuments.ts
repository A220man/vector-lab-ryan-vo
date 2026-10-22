import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Document } from '../types';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.listDocuments();
      setDocuments(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const uploadDocument = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.uploadDocument(file);
      await fetchDocuments();
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const indexDocument = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.indexDocument(id);
      await fetchDocuments();
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Indexing failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const incrementalUpdate = async (id: number, file: File) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.incrementalUpdateDocument(id, file);
      await fetchDocuments();
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Incremental update failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    uploadDocument,
    indexDocument,
    incrementalUpdate,
  };
}