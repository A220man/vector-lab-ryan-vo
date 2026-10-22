import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DocumentList } from '../components/DocumentList';
import { useDocuments } from '../hooks/useDocuments';

// Mock the hook
vi.mock('../hooks/useDocuments', () => ({
  useDocuments: vi.fn(),
}));

describe('DocumentList', () => {
  const mockUploadDocument = vi.fn();
  const mockIndexDocument = vi.fn();
  const mockIncrementalUpdate = vi.fn();
  const mockFetchDocuments = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useDocuments as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      documents: [
        { id: 1, filename: 'test.pdf', status: 'indexed', page_count: 10, version: 1, content_hash: 'abc', created_at: '2024-01-01T00:00:00Z' },
        { id: 2, filename: 'doc.txt', status: 'pending', page_count: 0, version: 1, content_hash: 'def', created_at: '2024-01-02T00:00:00Z' },
      ],
      loading: false,
      error: null,
      uploadDocument: mockUploadDocument,
      indexDocument: mockIndexDocument,
      incrementalUpdate: mockIncrementalUpdate,
      fetchDocuments: mockFetchDocuments,
    });
  });

  it('renders document list', () => {
    render(<DocumentList />);
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
    expect(screen.getByText('doc.txt')).toBeInTheDocument();
  });

  it('shows status badges', () => {
    render(<DocumentList />);
    expect(screen.getByText('indexed')).toBeInTheDocument();
    expect(screen.getByText('pending')).toBeInTheDocument();
  });

  it('calls uploadDocument on form submit', async () => {
    mockUploadDocument.mockResolvedValue({ id: 3 });
    render(<DocumentList />);
    
    const fileInput = screen.getByTestId('file-upload') as HTMLInputElement;
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    Object.defineProperty(fileInput, 'files', { value: [file] });
    
    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Upload Document'));
    
    await vi.waitFor(() => {
      expect(mockUploadDocument).toHaveBeenCalled();
    });
  });

  it('calls indexDocument when Index button clicked', async () => {
    mockIndexDocument.mockResolvedValue({});
    render(<DocumentList />);
    
    fireEvent.click(screen.getByText('Index'));
    
    await vi.waitFor(() => {
      expect(mockIndexDocument).toHaveBeenCalledWith(2);
    });
  });
});