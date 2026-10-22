import React, { useState } from 'react';
import { useDocuments } from '../hooks/useDocuments';

export const DocumentList: React.FC = () => {
  const { documents, loading, error, uploadDocument, indexDocument, incrementalUpdate, fetchDocuments } = useDocuments();
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [updateDocId, setUpdateDocId] = useState<number | null>(null);
  const [updateFile, setUpdateFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    try {
      await uploadDocument(selectedFile);
      setSelectedFile(null);
    } finally {
      setUploading(false);
    }
  };

  const handleIndex = async (docId: number) => {
    try {
      await indexDocument(docId);
    } catch (err) {
      console.error(err);
    }
  };

  const handleIncrementalUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!updateFile || !updateDocId) return;
    try {
      await incrementalUpdate(updateDocId, updateFile);
      setUpdateDocId(null);
      setUpdateFile(null);
    } catch (err) {
      console.error(err);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString();
  };

  const statusColor = (status: string) => {
    switch (status) {
      case 'indexed': return '#4caf50';
      case 'processing': return '#ff9800';
      case 'failed': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  if (loading && documents.length === 0) {
    return <div className="loading">Loading documents...</div>;
  }

  return (
    <div className="document-list">
      <div className="panel-header">
        <h2>Documents</h2>
        <button onClick={fetchDocuments} disabled={loading}>
          Refresh
        </button>
      </div>

      <form onSubmit={handleUpload} className="upload-form">
        <input
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileChange}
          disabled={uploading}
          data-testid="file-upload"
        />
        <button type="submit" disabled={uploading || !selectedFile}>
          {uploading ? 'Uploading...' : 'Upload Document'}
        </button>
      </form>

      {error && <div className="error-message">Error: {error}</div>}

      <div className="document-table-container">
        <table className="document-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Status</th>
              <th>Pages</th>
              <th>Version</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-state">
                  No documents uploaded yet. Upload a PDF to get started.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.filename}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: statusColor(doc.status) }}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td>{doc.page_count}</td>
                  <td>{doc.version}</td>
                  <td>{formatDate(doc.created_at)}</td>
                  <td>
                    <div className="action-buttons">
                      {doc.status !== 'indexed' && (
                        <button onClick={() => handleIndex(doc.id)} disabled={doc.status === 'processing'}>
                          {doc.status === 'processing' ? 'Processing...' : 'Index'}
                        </button>
                      )}
                      <button
                        onClick={() => setUpdateDocId(doc.id)}
                        className="secondary"
                      >
                        Update
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {updateDocId && updateFile && (
        <div className="update-form">
          <h3>Incremental Update: Document #{updateDocId}</h3>
          <p>Selected file: {updateFile.name}</p>
          <form onSubmit={handleIncrementalUpdate}>
            <button type="submit">Apply Incremental Update</button>
            <button type="button" onClick={() => { setUpdateDocId(null); setUpdateFile(null); }} className="secondary">
              Cancel
            </button>
          </form>
        </div>
      )}
    </div>
  );
};