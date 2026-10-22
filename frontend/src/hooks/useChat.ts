import { useState, useCallback } from 'react';
import { api } from '../api/client';
import type { ChatSession, ChatResponse } from '../types';

export function useChat(documentId?: number) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.listSessions(documentId);
      setSessions(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  const createSession = useCallback(async (message: string): Promise<ChatResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.chat({ message, document_id: documentId });
      await fetchSessions();
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, [documentId, fetchSessions]);

  const continueSession = useCallback(async (sessionId: number, message: string): Promise<ChatResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.chat({ message, session_id: sessionId });
      setCurrentSession(prev => prev?.id === sessionId ? { ...prev, messages: [...(prev.messages || []), { id: Date.now(), role: 'user', content: message, created_at: new Date().toISOString() }, { id: Date.now() + 1, role: 'assistant', content: response.data.response, usage: response.data.usage, created_at: new Date().toISOString() }] } : prev);
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSession = useCallback(async (sessionId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getSession(sessionId);
      setCurrentSession(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    sessions,
    currentSession,
    loading,
    error,
    fetchSessions,
    createSession,
    continueSession,
    loadSession,
    setCurrentSession,
  };
}