'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/use-auth';
import { jwtApiClient } from '@/services/auth/api-client';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your AI assistant. You can ask me to manage your tasks using natural language. For example, try "Add a task to buy groceries" or "Show me my tasks".',
      role: 'assistant',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading || !user) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the backend chat API using the dedicated method
      const response = await jwtApiClient.chatWithBot(user.id, inputValue);

      // Add AI response - the response structure is { conversation_id, response, tool_calls }
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response || 'I understood your request. How else can I help?',
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      console.error('Error name:', error?.name);
      console.error('Error message:', error?.message);
      console.error('Error code:', error?.code);
      console.error('Error response:', error?.response);
      console.error('Error request:', error?.request ? 'Request was made but no response' : 'No request made');

      // Check if error is an Axios error with response
      let errorMessageText = 'Sorry, I encountered an error processing your request. Please try again.';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any;
        if (axiosError.response?.data?.detail) {
          errorMessageText = `Error: ${axiosError.response.data.detail}`;
        } else if (axiosError.response?.status) {
          errorMessageText = `Server Error (${axiosError.response.status}): Unable to process your request`;
        }
      } else if (error && typeof error === 'object' && 'message' in error) {
        const genericError = error as Error;
        errorMessageText = `Error: ${genericError.message || 'Unknown error occurred'}`;
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: errorMessageText,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      <div className="border-b py-4 px-6">
        <h1 className="text-2xl font-bold">AI Task Assistant</h1>
        <p className="text-muted-foreground">
          Chat with your AI assistant to manage tasks using natural language
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground rounded-r-none'
                  : 'bg-muted rounded-l-none'
              }`}
            >
              <p>{message.content}</p>
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
            <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted rounded-l-none">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce delay-100"></div>
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me to manage your tasks (e.g., 'Add a task to buy groceries')..."
            className="flex-1"
            disabled={isLoading || !user}
          />
          <Button type="submit" disabled={isLoading || !user || !inputValue.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Examples: "Add a task to buy groceries", "Show me my tasks", "Mark task 3 as complete"
        </p>
      </div>
    </div>
  );
}