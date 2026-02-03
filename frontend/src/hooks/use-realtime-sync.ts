/**
 * Real-time Sync Hook
 *
 * Manages WebSocket connection and real-time task updates
 * Provides connection status and automatic reconnection
 */

import { useEffect, useState, useCallback } from 'react';
import { getWebSocketClient } from '@/services/websocket-client';
import { useAuth } from '@/hooks/use-auth';

export interface TaskUpdateEvent {
  event_id: string;
  event_type: 'sync' | 'created' | 'updated' | 'deleted' | 'completed';
  task_id: string;
  user_id: string;
  changes?: Record<string, any>;
  timestamp: string;
}

interface UseRealtimeSyncOptions {
  onTaskUpdate?: (event: TaskUpdateEvent) => void;
  onTaskCreated?: (event: TaskUpdateEvent) => void;
  onTaskUpdated?: (event: TaskUpdateEvent) => void;
  onTaskDeleted?: (event: TaskUpdateEvent) => void;
  onTaskCompleted?: (event: TaskUpdateEvent) => void;
  autoConnect?: boolean;
}

export function useRealtimeSync(options: UseRealtimeSyncOptions = {}) {
  const {
    onTaskUpdate,
    onTaskCreated,
    onTaskUpdated,
    onTaskDeleted,
    onTaskCompleted,
    autoConnect = true,
  } = options;

  const { user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [wsClient] = useState(() => getWebSocketClient());

  // Handle incoming messages
  const handleMessage = useCallback((data: any) => {
    try {
      const event = data as TaskUpdateEvent;

      // Only process events for the current user
      if (event.user_id && user?.id && event.user_id !== user.id) {
        return;
      }

      // Call the generic handler
      onTaskUpdate?.(event);

      // Call specific event handlers
      switch (event.event_type) {
        case 'created':
          onTaskCreated?.(event);
          break;
        case 'updated':
        case 'sync':
          onTaskUpdated?.(event);
          break;
        case 'deleted':
          onTaskDeleted?.(event);
          break;
        case 'completed':
          onTaskCompleted?.(event);
          break;
      }
    } catch (error) {
      console.error('[useRealtimeSync] Failed to handle message:', error);
    }
  }, [user?.id, onTaskUpdate, onTaskCreated, onTaskUpdated, onTaskDeleted, onTaskCompleted]);

  // Connect/disconnect based on auth status and autoConnect
  useEffect(() => {
    if (!autoConnect) return;

    if (user) {
      // Get token from localStorage
      const token = localStorage.getItem('access_token');
      // Connect with user's ID and token
      wsClient.connect(user.id, token || undefined);
    } else {
      // Disconnect if user logs out
      wsClient.disconnect();
    }

    return () => {
      wsClient.disconnect();
    };
  }, [user, autoConnect, wsClient]);

  // Subscribe to messages
  useEffect(() => {
    const unsubscribeMessage = wsClient.onMessage(handleMessage);
    const unsubscribeConnectionState = wsClient.onConnectionStateChange(setIsConnected);

    return () => {
      unsubscribeMessage();
      unsubscribeConnectionState();
    };
  }, [wsClient, handleMessage]);

  // Manual connect/disconnect functions
  const connect = useCallback(() => {
    if (user?.id) {
      const token = localStorage.getItem('access_token');
      wsClient.connect(user.id, token || undefined);
    }
  }, [wsClient, user]);

  const disconnect = useCallback(() => {
    wsClient.disconnect();
  }, [wsClient]);

  const send = useCallback((data: any) => {
    wsClient.send(data);
  }, [wsClient]);

  return {
    isConnected,
    connect,
    disconnect,
    send,
  };
}
