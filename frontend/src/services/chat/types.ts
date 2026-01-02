/**
 * Type definitions for ChatKit integration
 */

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  thread_id?: string;
}

export interface ChatWidget {
  id: string;
  type: string;
  payload: any;
  timestamp: Date;
  thread_id?: string;
}

export interface ChatEvent {
  type: 'message' | 'widget' | 'completion' | 'error';
  data: {
    content?: string;
    widget?: ChatWidget;
    status?: string;
    error?: string;
  };
}

export interface ChatThread {
  id: string;
  user_id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  metadata?: Record<string, any>;
}

export interface ChatAction {
  id: string;
  widget_id: string;
  thread_id: string;
  type: string;
  payload: Record<string, any>;
  created_at: Date;
  processed_at?: Date;
  result?: Record<string, any>;
}

export interface ChatActionRequest {
  thread_id: string;
  action: {
    type: string;
    widget_id: string;
    payload: Record<string, any>;
  };
}

export interface ChatActionResponse {
  status: 'success' | 'error';
  thread_id: string;
  action_id: string;
  result?: any;
}

export interface ChatKitConfig {
  serverUrl: string;
  authToken: string;
  userId: string;
}