import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { IndexNode, SearchResult } from '../types';

export function useIndex(documentId: number | null) {
  const [tree, setTree] = useState<IndexNode[]>([]);
  const [leaves, setLeaves] = useState<IndexNode[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTree = async () => {
    if (!documentId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.getIndexTree(documentId);
      setTree(response.data.tree?.nodes || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch index tree');
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaves = async () => {
    if (!documentId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.getIndexLeaves(documentId);
      setLeaves(response.data.leaves || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch leaves');
    } finally {
      setLoading(false);
    }
  };

  const search = async (query: string) => {
    if (!documentId || !query.trim()) {
      setSearchResults([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await api.searchIndex(documentId, query);
      setSearchResults(response.data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (documentId) {
      fetchTree();
      fetchLeaves();
    } else {
      setTree([]);
      setLeaves([]);
      setSearchResults([]);
    }
  }, [documentId]);

  return {
    tree,
    leaves,
    searchResults,
    loading,
    error,
    fetchTree,
    fetchLeaves,
    search,
  };
}