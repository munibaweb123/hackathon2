/**
 * WebSocket Client Service
 *
 * Manages WebSocket connections for real-time task updates
 * Implements reconnection logic and event handling
 */

type MessageHandler = (data: any) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private currentUserId: string | null = null;
  private currentToken: string | undefined = undefined;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private messageHandlers: Set<MessageHandler> = new Set();
  private connectionStateHandlers: Set<(connected: boolean) => void> = new Set();
  private shouldReconnect = true;

  constructor(url: string) {
    this.url = url;
  }

  /**
   * Connect to WebSocket server
   */
  connect(userId: string, token?: string): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      console.log('[WS] Already connected or connecting');
      return;
    }

    // Store userId and token for potential reconnection
    this.currentUserId = userId;
    this.currentToken = token;

    try {
      // Construct the URL with userId and optionally append token
      const baseUrl = this.url.endsWith('/') ? this.url.slice(0, -1) : this.url;
      const wsUrlWithUserId = `${baseUrl}/${userId}`;
      const wsUrl = token ? `${wsUrlWithUserId}?token=${token}` : wsUrlWithUserId;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[WS] Connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.notifyConnectionState(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WS] Message received:', data);
          this.messageHandlers.forEach(handler => handler(data));
        } catch (error) {
          console.error('[WS] Failed to parse message:', error);
        }
      };

      this.ws.onerror = (error) => {
        // Log more detailed error information
        console.error('[WS] Error:', {
          error: error,
          message: error instanceof ErrorEvent ? error.message : 'Unknown error',
          type: error instanceof ErrorEvent ? error.type : 'Unknown type',
          target: error instanceof ErrorEvent ? error.target : undefined,
        });
      };

      this.ws.onclose = (event) => {
        console.log('[WS] Disconnected:', event.code, event.reason);
        this.notifyConnectionState(false);

        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      };
    } catch (error) {
      console.error('[WS] Connection error:', {
        error: error,
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
      });
      this.notifyConnectionState(false);

      if (this.shouldReconnect) {
        this.scheduleReconnect();
      }
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    // Clear stored userId and token
    this.currentUserId = null;
    this.currentToken = undefined;

    this.notifyConnectionState(false);
  }

  /**
   * Send a message to the server
   */
  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('[WS] Cannot send message: not connected');
    }
  }

  /**
   * Register a message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Register a connection state handler
   */
  onConnectionStateChange(handler: (connected: boolean) => void): () => void {
    this.connectionStateHandlers.add(handler);

    // Immediately notify current state
    handler(this.isConnected());

    // Return unsubscribe function
    return () => {
      this.connectionStateHandlers.delete(handler);
    };
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Schedule a reconnection attempt with exponential backoff
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.shouldReconnect && this.currentUserId) {
        this.connect(this.currentUserId, this.currentToken);
      }
    }, delay);
  }

  /**
   * Notify all connection state handlers
   */
  private notifyConnectionState(connected: boolean): void {
    this.connectionStateHandlers.forEach(handler => handler(connected));
  }
}

// Singleton instance
let wsClient: WebSocketClient | null = null;

/**
 * Get the WebSocket client singleton
 */
export function getWebSocketClient(): WebSocketClient {
  if (!wsClient) {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/tasks/';
    wsClient = new WebSocketClient(wsUrl);
  }
  return wsClient;
}
