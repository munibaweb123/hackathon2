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

export class ChatKitClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  async *streamChat(userId: string, message: string) {
    const token = await getJwtToken();

    const response = await fetch(`${this.baseUrl}/api/chat/chatkit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        user_id: userId,
        thread_id: 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          const r = Math.random() * 16 | 0;
          const v = c === 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
        }),
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
}

export const chatKitClient = new ChatKitClient();