import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatView } from '../components/ChatView';
import { useChat } from '../hooks/useChat';

vi.mock('../hooks/useChat', () => ({
  useChat: vi.fn(),
}));

describe('ChatView', () => {
  const mockCreateSession = vi.fn();
  const mockContinueSession = vi.fn();
  const mockLoadSession = vi.fn();
  const mockFetchSessions = vi.fn();
  const mockSetCurrentSession = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useChat as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      sessions: [],
      currentSession: null,
      loading: false,
      error: null,
      fetchSessions: mockFetchSessions,
      createSession: mockCreateSession,
      continueSession: mockContinueSession,
      loadSession: mockLoadSession,
      setCurrentSession: mockSetCurrentSession,
    });
  });

  it('renders welcome state when no session', () => {
    render(<ChatView documentId={1} />);
    expect(screen.getByText('Start a conversation')).toBeInTheDocument();
  });

  it('calls createSession on send', async () => {
    mockCreateSession.mockResolvedValue({
      response: 'Hello!',
      session_id: 1,
      usage: { input_tokens: 10, output_tokens: 20, complete: 1 },
    });
    mockLoadSession.mockResolvedValue({});

    render(<ChatView documentId={1} />);
    const textarea = screen.getByPlaceholderText('Ask a question...');
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByText('Send'));

    await vi.waitFor(() => {
      expect(mockCreateSession).toHaveBeenCalledWith('Hello');
    });
  });

  it('shows sessions in sidebar', () => {
    (useChat as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      sessions: [
        { id: 1, title: 'Test Chat', updated_at: '2024-01-01T12:00:00Z' },
      ],
      currentSession: null,
      loading: false,
      error: null,
      fetchSessions: mockFetchSessions,
      createSession: mockCreateSession,
      continueSession: mockContinueSession,
      loadSession: mockLoadSession,
      setCurrentSession: mockSetCurrentSession,
    });

    render(<ChatView documentId={1} />);
    expect(screen.getByText('Test Chat')).toBeInTheDocument();
  });
});