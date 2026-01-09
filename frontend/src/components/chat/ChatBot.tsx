'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, User, Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { getJwtToken } from '@/lib/auth-client';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  widget?: Widget;
}

interface Widget {
  type: string;
  status?: { icon: string; text: string };
  children?: WidgetChild[];
}

interface WidgetChild {
  type: string;
  value?: string;
  weight?: string;
  size?: string;
  lineThrough?: boolean;
  color?: string;
  children?: WidgetChild[];
}

interface ChatBotProps {
  userId: string;
  onTaskChange?: () => void;
}

const STARTER_PROMPTS = [
  { label: 'Show my tasks', prompt: 'Show my tasks', icon: '📋' },
  { label: 'Add a task', prompt: 'Add task ', icon: '➕' },
  { label: 'Get help', prompt: 'Help', icon: '❓' },
];

export function ChatBot({ userId, onTaskChange }: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm your AI Task Assistant. I can help you manage your tasks. Try:\n\n• \"Show my tasks\" - to see your tasks\n• \"Add task [title]\" - to create a new task\n• \"Complete task [number]\" - to mark a task as done\n• \"Delete task [number]\" - to remove a task\n\nHow can I help you today?",
      role: 'assistant',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId] = useState(() => {
    // Generate a proper UUID format for the thread ID
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const processStreamResponse = async (response: Response): Promise<Message | null> => {
    if (!response.body) return null;

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let accumulatedContent = '';
    let widget: Widget | undefined;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete lines from the Server-Sent Events stream
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          const trimmedLine = line.trim();

          // Look for Server-Sent Event format: "data: <json_payload>"
          if (trimmedLine.startsWith('data: ')) {
            try {
              // Extract the JSON payload after "data: "
              const dataPayload = trimmedLine.substring(6); // Remove "data: " prefix

              if (dataPayload && dataPayload !== '[DONE]') {
                const event = JSON.parse(dataPayload);

                if (event.type === 'message' && event.data?.content) {
                  accumulatedContent += event.data.content + '\n';
                } else if (event.type === 'widget' && event.data?.widget) {
                  widget = event.data.widget;
                } else if (event.type === 'completion') {
                  // End of stream marker
                  break;
                }
              }
            } catch (e) {
              // Skip invalid JSON lines but log for debugging
              console.debug('Skipping invalid SSE data:', trimmedLine);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    if (accumulatedContent || widget) {
      return {
        id: `msg-${Date.now()}`,
        content: accumulatedContent.trim(),
        role: 'assistant',
        timestamp: new Date(),
        widget,
      };
    }

    return null;
  };

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: messageText,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Use the ChatKitClient instead of direct fetch to ensure JWT token is included
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/chatkit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getJwtToken()}`,  // Include JWT token
        },
        body: JSON.stringify({
          input: messageText,  // Using 'input' field as expected by ChatKit server
          thread_id: threadId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const assistantMessage = await processStreamResponse(response);

      if (assistantMessage) {
        setMessages(prev => [...prev, assistantMessage]);

        // Notify parent if task might have changed
        if (messageText.toLowerCase().includes('add') ||
            messageText.toLowerCase().includes('complete') ||
            messageText.toLowerCase().includes('delete')) {
          onTaskChange?.();
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handlePromptClick = (prompt: string) => {
    if (prompt.endsWith(' ')) {
      setInputValue(prompt);
      inputRef.current?.focus();
    } else {
      sendMessage(prompt);
    }
  };

  const renderWidget = (widget: Widget) => {
    if (widget.type === 'list' && widget.children) {
      return (
        <div className="mt-3 space-y-2">
          {widget.status && (
            <div className="text-sm font-medium text-muted-foreground mb-2">
              {widget.status.text}
            </div>
          )}
          {widget.children.map((child, index) => (
            <div key={index} className="bg-muted/50 rounded-lg p-3 space-y-1">
              {child.children?.map((item, itemIndex) => (
                <div
                  key={itemIndex}
                  className={cn(
                    'text-sm',
                    item.weight === 'bold' && 'font-semibold',
                    item.size === 'lg' && 'text-base',
                    item.size === 'sm' && 'text-xs',
                    item.lineThrough && 'line-through',
                    item.color === 'secondary' && 'text-muted-foreground',
                    item.color === 'emphasis' && 'text-foreground'
                  )}
                >
                  {item.value}
                </div>
              ))}
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="flex flex-col h-full bg-background rounded-xl border shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b bg-muted/30">
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary">
          <Bot className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h2 className="font-semibold">AI Task Assistant</h2>
          <p className="text-xs text-muted-foreground">Powered by OpenAI</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              'flex gap-3',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
            )}
            <div
              className={cn(
                'max-w-[85%] rounded-2xl px-4 py-2.5',
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground rounded-br-md'
                  : 'bg-muted rounded-bl-md'
              )}
            >
              <p className="whitespace-pre-wrap text-sm">{message.content}</p>
              {message.widget && renderWidget(message.widget)}
            </div>
            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                <User className="h-4 w-4 text-secondary-foreground" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Starter Prompts */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <div className="flex flex-wrap gap-2">
            {STARTER_PROMPTS.map((prompt, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => handlePromptClick(prompt.prompt)}
              >
                <span className="mr-1">{prompt.icon}</span>
                {prompt.label}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t bg-muted/30">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-background"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading || !inputValue.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
