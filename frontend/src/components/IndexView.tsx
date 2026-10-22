import React, { useState } from 'react';
import { useIndex } from '../hooks/useIndex';
import { IndexTree } from './IndexTree';
import type { IndexNode } from '../types';

export const IndexView: React.FC<{ documentId: number | null }> = ({ documentId }) => {
  const { tree, leaves, searchResults, loading, error, search } = useIndex(documentId);
  const [selectedNode, setSelectedNode] = useState<IndexNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'tree' | 'leaves' | 'search'>('tree');

  if (!documentId) {
    return (
      <div className="index-view">
        <div className="empty-state">Select a document to view its index</div>
      </div>
    );
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      search(searchQuery);
      setViewMode('search');
    }
  };

  const handleNodeSelect = (node: IndexNode) => {
    setSelectedNode(node);
    setViewMode('tree');
  };

  return (
    <div className="index-view">
      <div className="panel-header">
        <h2>Document Index</h2>
        <div className="view-tabs">
          <button
            className={viewMode === 'tree' ? 'active' : ''}
            onClick={() => setViewMode('tree')}
          >
            Tree
          </button>
          <button
            className={viewMode === 'leaves' ? 'active' : ''}
            onClick={() => setViewMode('leaves')}
          >
            Leaves
          </button>
        </div>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search index..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !searchQuery.trim()}>
          Search
        </button>
      </form>

      {error && <div className="error-message">Error: {error}</div>}

      {viewMode === 'tree' && (
        <div className="tree-container">
          <IndexTree
            nodes={tree}
            selectedNodeId={selectedNode?.node_id}
            onSelectNode={handleNodeSelect}
          />
        </div>
      )}

      {viewMode === 'leaves' && (
        <div className="leaves-container">
          {leaves.length === 0 ? (
            <div className="empty-state">No leaf nodes found</div>
          ) : (
            <ul className="leaves-list">
              {leaves.map((leaf) => (
                <li key={leaf.node_id} className="leaf-item">
                  <span className="leaf-structure">{leaf.structure}</span>
                  <span className="leaf-title">{leaf.title}</span>
                  <span className="leaf-pages">
                    {leaf.start_page !== undefined && leaf.end_page !== undefined
                      ? `pp. ${leaf.start_page}–${leaf.end_page}`
                      : ''}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {viewMode === 'search' && (
        <div className="search-results">
          {searchResults.length === 0 && searchQuery.trim() ? (
            <div className="empty-state">No results for "{searchQuery}"</div>
          ) : (
            <ul className="results-list">
              {searchResults.map((result) => (
                <li key={result.node_id} className="result-item">
                  <span className="result-structure">{result.structure}</span>
                  <span className="result-title">{result.title}</span>
                  <span className={`result-match-type ${result.match_type}`}>
                    {result.match_type}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {selectedNode && (
        <div className="node-detail-panel">
          <h3>Node Detail</h3>
          <p><strong>Structure:</strong> {selectedNode.structure}</p>
          <p><strong>Title:</strong> {selectedNode.title}</p>
          <p><strong>Level:</strong> {selectedNode.level}</p>
          {selectedNode.start_page && selectedNode.end_page && (
            <p><strong>Pages:</strong> {selectedNode.start_page}–{selectedNode.end_page}</p>
          )}
          {selectedNode.summary && (
            <div className="node-summary">
              <h4>Summary</h4>
              <p>{selectedNode.summary}</p>
            </div>
          )}
          {selectedNode.content && (
            <div className="node-content">
              <h4>Content</h4>
              <pre>{selectedNode.content}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};