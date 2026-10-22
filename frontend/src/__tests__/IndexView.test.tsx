import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { IndexView } from '../components/IndexView';
import { useIndex } from '../hooks/useIndex';

vi.mock('../hooks/useIndex', () => ({
  useIndex: vi.fn(),
}));

describe('IndexView', () => {
  const mockSearch = vi.fn();
  const mockFetchTree = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useIndex as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      tree: [
        {
          node_id: '1',
          structure: '1',
          title: 'Chapter 1',
          level: 0,
          nodes: [
            { node_id: '1.1', structure: '1.1', title: 'Section 1.1', level: 1, nodes: [] },
          ],
        },
      ],
      leaves: [
        { node_id: '1.1', structure: '1.1', title: 'Section 1.1', level: 1, start_page: 1, end_page: 2 },
      ],
      searchResults: [],
      loading: false,
      error: null,
      fetchTree: mockFetchTree,
      fetchLeaves: vi.fn(),
      search: mockSearch,
    });
  });

  it('renders tree view by default', () => {
    render(<IndexView documentId={1} />);
    expect(screen.getByText('Document Index')).toBeInTheDocument();
    expect(screen.getByText('Chapter 1')).toBeInTheDocument();
    expect(screen.getByText('Section 1.1')).toBeInTheDocument();
  });

  it('switches to leaves view', () => {
    render(<IndexView documentId={1} />);
    fireEvent.click(screen.getByText('Leaves'));
    expect(screen.getByText('Section 1.1')).toBeInTheDocument();
    expect(screen.getByText('pp. 1–2')).toBeInTheDocument();
  });

  it('shows empty state when no document selected', () => {
    render(<IndexView documentId={null} />);
    expect(screen.getByText('Select a document to view its index')).toBeInTheDocument();
  });

  it('calls search on form submit', () => {
    render(<IndexView documentId={1} />);
    const input = screen.getByPlaceholderText('Search index...');
    fireEvent.change(input, { target: { value: 'test query' } });
    fireEvent.click(screen.getByText('Search'));
    expect(mockSearch).toHaveBeenCalledWith('test query');
  });
});