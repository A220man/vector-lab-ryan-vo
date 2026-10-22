import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import type { ChatMessage } from '../types';

export const ChatView: React.FC<{ documentId?: number }> = ({ documentId }) => {
  const { sessions, currentSession, loading, error, fetchSessions, createSession, continueSession, loadSession, setCurrentSession } = useChat(documentId);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const message = inputMessage;
    setInputMessage('');

    if (currentSession) {
      await continueSession(currentSession.id, message);
    } else {
      const response = await createSession(message);
      if (response) {
        await loadSession(response.session_id);
      }
    }
  };

  const handleNewChat = () => {
    setCurrentSession(null);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString();
  };

  const renderUsage = (usage?: ChatMessage['usage']) => {
    if (!usage) return null;
    return (
      <div className="message-usage">
        <span>In: {usage.input_tokens ?? '?'}</span>
        <span>Out: {usage.output_tokens ?? '?'}</span>
        {usage.cache_read_tokens && <span>Cache Read: {usage.cache_read_tokens}</span>}
        {usage.cache_write_tokens && <span>Cache Write: {usage.cache_write_tokens}</span>}
        {usage.reasoning_tokens && <span>Reasoning: {usage.reasoning_tokens}</span>}
        <span className={`usage-complete ${usage.complete === 1 ? 'complete' : usage.complete === 0 ? 'partial' : 'unknown'}`}>
          {usage.complete === 1 ? 'Complete' : usage.complete === 0 ? 'Partial' : 'Unknown'}
        </span>
      </div>
    );
  };

  return (
    <div className="chat-view">
      <div className="panel-header">
        <h2>Chat</h2>
        <button onClick={handleNewChat} className="secondary">
          New Chat
        </button>
      </div>

      <div className="sessions-sidebar">
        <h3>Sessions</h3>
        {sessions.length === 0 ? (
          <div className="empty-state">No chat sessions yet</div>
        ) : (
          <ul className="sessions-list">
            {sessions.map((session) => (
              <li
                key={session.id}
                className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                onClick={() => loadSession(session.id)}
              >
                <span className="session-title">{session.title}</span>
                <span className="session-date">{formatDate(session.updated_at)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="chat-main">
        {currentSession ? (
          <>
            <div className="messages-container">
              {currentSession.messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div className="message-header">
                    <span className="message-role">{msg.role}</span>
                    <span className="message-time">{formatDate(msg.created_at)}</span>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                  {msg.role === 'assistant' && renderUsage(msg.usage)}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} className="chat-input-form">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask a question about the document..."
                disabled={loading}
                rows={3}
              />
              <button type="submit" disabled={loading || !inputMessage.trim()}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </>
        ) : (
          <div className="chat-welcome">
            <h3>Start a conversation</h3>
            <p>Select a document and click "New Chat" or type a message below.</p>
            <form onSubmit={handleSend} className="chat-input-form">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask a question..."
                disabled={loading}
                rows={3}
              />
              <button type="submit" disabled={loading || !inputMessage.trim()}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        )}
      </div>

      {error && <div className="error-message">Error: {error}</div>}
    </div>
  );
};