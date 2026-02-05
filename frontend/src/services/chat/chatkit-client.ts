import { getJwtToken } from '@/lib/auth-client';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface ChatWidget {
  id: string;
  type: string;
  data: any;
  timestamp: Date;
}

export interface ChatEvent {
  type: 'message' | 'widget' | 'completion';
  data: {
    content?: string;
    widget?: any;
    status?: string;
  };
}

export interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
};

export class ChatKitClient {
  private baseUrl: string;
  private retryConfig: RetryConfig;
  private connectionStatus: 'connected' | 'disconnected' | 'reconnecting' = 'disconnected';
  private onConnectionStatusChange?: (status: string) => void;

  constructor(config?: { retryConfig?: Partial<RetryConfig>; onConnectionStatusChange?: (status: string) => void }) {
    this.baseUrl = typeof window !== 'undefined' ? window.location.origin : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');
    this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...config?.retryConfig };
    this.onConnectionStatusChange = config?.onConnectionStatusChange;
  }

  /**
   * Calculate exponential backoff delay with jitter
   */
  private calculateBackoff(attempt: number): number {
    const delay = Math.min(
      this.retryConfig.baseDelay * Math.pow(2, attempt),
      this.retryConfig.maxDelay
    );
    // Add jitter (±25%)
    const jitter = delay * 0.25 * (Math.random() * 2 - 1);
    return Math.floor(delay + jitter);
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Update connection status and notify listeners
   */
  private setConnectionStatus(status: 'connected' | 'disconnected' | 'reconnecting'): void {
    this.connectionStatus = status;
    this.onConnectionStatusChange?.(status);
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): string {
    return this.connectionStatus;
  }

  /**
   * Check if the API is reachable (health check)
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Execute a fetch request with retry logic (T071)
   */
  private async fetchWithRetry(
    url: string,
    options: RequestInit,
    retryCount = 0
  ): Promise<Response> {
    try {
      this.setConnectionStatus(retryCount > 0 ? 'reconnecting' : 'connected');
      const response = await fetch(url, options);

      // If we get a 5xx error, retry
      if (response.status >= 500 && retryCount < this.retryConfig.maxRetries) {
        const delay = this.calculateBackoff(retryCount);
        console.warn(`Server error ${response.status}, retrying in ${delay}ms (attempt ${retryCount + 1}/${this.retryConfig.maxRetries})`);
        await this.sleep(delay);
        return this.fetchWithRetry(url, options, retryCount + 1);
      }

      this.setConnectionStatus('connected');
      return response;
    } catch (error) {
      // Network errors - retry with backoff
      if (retryCount < this.retryConfig.maxRetries) {
        const delay = this.calculateBackoff(retryCount);
        console.warn(`Network error, retrying in ${delay}ms (attempt ${retryCount + 1}/${this.retryConfig.maxRetries}):`, error);
        this.setConnectionStatus('reconnecting');
        await this.sleep(delay);
        return this.fetchWithRetry(url, options, retryCount + 1);
      }

      this.setConnectionStatus('disconnected');
      throw error;
    }
  }

  /**
   * Generate a UUID v4 for thread IDs
   */
  private generateThreadId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Stream chat messages from the server using Server-Sent Events
   * Includes retry logic for failed requests (T071)
   */
  async *streamChat(userId: string, message: string, threadId?: string) {
    const token = await getJwtToken();
    const actualThreadId = threadId || this.generateThreadId();

    const response = await this.fetchWithRetry(`${this.baseUrl}/api/chat/chatkit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        input: message, // Support both field names for compatibility
        user_id: userId,
        thread_id: actualThreadId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process each complete line
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)); // Remove 'data: ' prefix

              yield data as ChatEvent;
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async sendMessage(userId: string, message: string): Promise<{ messages: ChatMessage[], widgets: ChatWidget[] }> {
    const messages: ChatMessage[] = [];
    const widgets: ChatWidget[] = [];

    for await (const event of this.streamChat(userId, message)) {
      if (event.type === 'message' && event.data.content) {
        messages.push({
          id: `msg-${Date.now()}-${Math.random()}`,
          content: event.data.content,
          role: 'assistant',
          timestamp: new Date(),
        });
      } else if (event.type === 'widget' && event.data.widget) {
        widgets.push({
          id: `widget-${Date.now()}-${Math.random()}`,
          type: event.data.widget.type || 'unknown',
          data: event.data.widget,
          timestamp: new Date(),
        });
      } else if (event.type === 'completion') {
        break;
      }
    }

    return { messages, widgets };
  }

  /**
   * Load conversation history from the server (T078)
   *
   * @param userId - The user's ID
   * @param threadId - Optional thread ID to load specific conversation
   * @param limit - Maximum number of messages to load (default 50)
   * @returns Promise with conversation history
   */
  async loadConversationHistory(
    userId: string,
    threadId?: string,
    limit = 50
  ): Promise<{ messages: ChatMessage[]; threadId: string | null }> {
    try {
      const token = await getJwtToken();
      const url = new URL(`${this.baseUrl}/api/chat/history`);
      url.searchParams.set('user_id', userId);
      url.searchParams.set('limit', limit.toString());
      if (threadId) {
        url.searchParams.set('thread_id', threadId);
      }

      const response = await this.fetchWithRetry(url.toString(), {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        // If endpoint doesn't exist or returns error, return empty history
        if (response.status === 404) {
          return { messages: [], threadId: null };
        }
        throw new Error(`Failed to load conversation history: ${response.status}`);
      }

      const data = await response.json();

      // Transform server response to ChatMessage format
      const messages: ChatMessage[] = (data.messages || []).map((msg: any) => ({
        id: msg.id || `msg-${Date.now()}-${Math.random()}`,
        content: msg.content || '',
        role: msg.role as 'user' | 'assistant',
        timestamp: new Date(msg.timestamp || msg.created_at || Date.now()),
      }));

      return {
        messages,
        threadId: data.thread_id || threadId || null,
      };
    } catch (error) {
      console.error('Error loading conversation history:', error);
      // Return empty history on error - graceful degradation (T070)
      return { messages: [], threadId: null };
    }
  }

  /**
   * Get or create a thread for a user
   *
   * @param userId - The user's ID
   * @returns Promise with thread ID
   */
  async getOrCreateThread(userId: string): Promise<string> {
    try {
      const token = await getJwtToken();
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/chat/thread`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (!response.ok) {
        // If endpoint doesn't exist, generate a local thread ID
        if (response.status === 404) {
          return this.generateThreadId();
        }
        throw new Error(`Failed to get or create thread: ${response.status}`);
      }

      const data = await response.json();
      return data.thread_id || this.generateThreadId();
    } catch (error) {
      console.error('Error getting/creating thread:', error);
      // Graceful degradation - generate local thread ID (T070)
      return this.generateThreadId();
    }
  }
}

// Create a singleton instance with default configuration
export const chatKitClient = new ChatKitClient();

// Export a factory function for custom configurations
export function createChatKitClient(config?: {
  retryConfig?: Partial<RetryConfig>;
  onConnectionStatusChange?: (status: string) => void;
}): ChatKitClient {
  return new ChatKitClient(config);
}
