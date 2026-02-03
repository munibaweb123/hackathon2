/**
 * Connection Status Component
 *
 * Displays real-time connection status indicator
 * Shows connected/disconnected state with appropriate styling
 */

'use client';

import { useRealtimeSync } from '@/hooks/use-realtime-sync';
import { useAuth } from '@/hooks/use-auth';

export function ConnectionStatus() {
  const { user } = useAuth();
  const { isConnected } = useRealtimeSync({
    autoConnect: false
  });

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 text-sm">
      <div
        className={`w-2 h-2 rounded-full ${
          isConnected && user
            ? 'bg-green-500 animate-pulse'
            : 'bg-red-500'
        }`}
        aria-label={isConnected && user ? 'Connected' : 'Disconnected'}
      />
      <span className="text-muted-foreground font-medium">
        {(isConnected && user) ? 'Live' : 'Offline'}
      </span>
    </div>
  );
}

export function ConnectionStatusBadge() {
  const { user } = useAuth();
  const { isConnected } = useRealtimeSync({ autoConnect: false });

  if (isConnected || !user) {
    return null; // Don't show anything when connected or not logged in
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 px-4 py-2 rounded-lg bg-destructive text-destructive-foreground shadow-lg">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      <span className="font-medium">Connection Lost</span>
    </div>
  );
}
