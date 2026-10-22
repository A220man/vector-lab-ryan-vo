import React, { useState } from 'react';
import { DocumentList } from './DocumentList';
import { IndexView } from './IndexView';
import { ChatView } from './ChatView';
import { useDocuments } from '../hooks/useDocuments';
import type { Document } from '../types';

export const Dashboard: React.FC = () => {
  const { documents: _documents } = useDocuments();
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [view, setView] = useState<'documents' | 'index' | 'chat'>('documents');

  const handleDocSelect = (doc: Document) => {
    setSelectedDoc(doc);
    setView('index');
  };

  return (
    <div className="dashboard">
      <header className="app-header">
        <h1>PageIndex</h1>
        <p className="subtitle">Vectorless, Reasoning-based RAG</p>
        <nav className="main-nav">
          <button
            className={view === 'documents' ? 'active' : ''}
            onClick={() => handleDocSelect(null as unknown as Document)}
          >
            Documents
          </button>
          <button
            className={view === 'index' ? 'active' : ''}
            onClick={() => setView('index')}
            disabled={!selectedDoc}
          >
            Index
          </button>
          <button
            className={view === 'chat' ? 'active' : ''}
            onClick={() => setView('chat')}
            disabled={!selectedDoc}
          >
            Chat
          </button>
        </nav>
      </header>

      <main className="app-main">
        {view === 'documents' && (
          <DocumentList />
        )}
        {view === 'index' && selectedDoc && (
          <IndexView documentId={selectedDoc.id} />
        )}

        {view === 'chat' && selectedDoc && (
          <ChatView documentId={selectedDoc.id} />
        )}

        {view !== 'documents' && !selectedDoc && (
          <div className="empty-state">
            Please select a document from the Documents view first.
          </div>
        )}
      </main>
    </div>
  );
};