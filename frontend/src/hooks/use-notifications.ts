'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from './use-auth';

interface Notification {
  id: string;
  type: 'reminder' | 'task_update' | 'system';
  title: string;
  message?: string;
  task_id?: number;
  timestamp: string;
  read: boolean;
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  addNotification: (notification: Omit<Notification, 'id' | 'read' | 'timestamp'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotification: (id: string) => void;
  clearAllNotifications: () => void;
}

export function useNotifications(): UseNotificationsReturn {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Calculate unread count
  const unreadCount = notifications.filter(n => !n.read).length;

  // Add a new notification
  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'read' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notificationData,
      id: Math.random().toString(36).substring(2, 9),
      read: false,
      timestamp: new Date().toISOString(),
    };

    setNotifications(prev => [newNotification, ...prev]);
  }, []);

  // Mark a single notification as read
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  }, []);

  // Mark all notifications as read
  const markAllAsRead = useCallback(() => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  // Clear a single notification
  const clearNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Clear all notifications
  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Handle WebSocket connection
  useEffect(() => {
    if (!user?.id) {
      setIsConnected(false);
      return;
    }

    const connectWebSocket = () => {
      // In a real implementation, this would connect to your WebSocket endpoint
      // For now, we'll simulate WebSocket functionality
      try {
        // For demonstration purposes, we'll simulate the connection status
        setIsConnected(true);

        // Simulate receiving notifications
        const mockNotification: Notification = {
          id: 'mock-reminder-1',
          type: 'reminder',
          title: 'Task Reminder',
          message: 'Your task "Buy groceries" is due today',
          task_id: 1,
          timestamp: new Date().toISOString(),
          read: false,
        };

        // In a real app, you would set up actual WebSocket connection here
        // wsRef.current = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/ws/${user.id}`);

        // wsRef.current.onopen = () => {
        //   setIsConnected(true);
        // };

        // wsRef.current.onmessage = (event) => {
        //   const data = JSON.parse(event.data);
        //   addNotification(data);
        // };

        // wsRef.current.onclose = () => {
        //   setIsConnected(false);
        //   // Attempt to reconnect after 3 seconds
        //   if (reconnectTimeoutRef.current) {
        //     clearTimeout(reconnectTimeoutRef.current);
        //   }
        //   reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
        // };

        // wsRef.current.onerror = (error) => {
        //   console.error('WebSocket error:', error);
        //   setIsConnected(false);
        // };
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    // Cleanup function
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [user?.id, addNotification]);

  return {
    notifications,
    unreadCount,
    isConnected,
    addNotification,
    markAsRead,
    markAllAsRead,
    clearNotification,
    clearAllNotifications,
  };
}