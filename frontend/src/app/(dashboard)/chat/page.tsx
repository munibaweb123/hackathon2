'use client';

import { useCallback } from 'react';
import { ChatBot } from '@/components/chat/ChatBot';
import { useAuth } from '@/hooks/use-auth';

export default function ChatPage() {
  const { user } = useAuth();

  const handleTaskChange = useCallback(() => {
    // This could trigger a refresh of task lists in other components
    if (process.env.NODE_ENV !== "production") {
      console.debug("[ChatPage] Task changed, may need to refresh task lists");
    }
  }, []);

  if (!user) {
    return (
      <div className="flex flex-col h-full items-center justify-center">
        <p className="text-muted-foreground">Please sign in to use the AI assistant.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 p-4 max-w-4xl mx-auto w-full">
        <ChatBot
          userId={user.id}
          onTaskChange={handleTaskChange}
        />
      </div>
    </div>
  );
}
