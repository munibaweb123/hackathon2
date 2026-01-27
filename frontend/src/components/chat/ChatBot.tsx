'use client';

import { useState, useRef, useEffect, useCallback, KeyboardEvent } from 'react';
import { Send, Bot, User, Loader2, RefreshCw, Mic, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { getJwtToken } from '@/lib/auth-client';

// Web Speech API types
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: ((event: Event) => void) | null;
  onaudiostart: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

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

// Keyboard shortcuts for accessibility (T068)
const KEYBOARD_SHORTCUTS = {
  SEND: 'Enter',
  FOCUS_INPUT: '/',
  SCROLL_UP: 'ArrowUp',
  SCROLL_DOWN: 'ArrowDown',
};

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
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [announcementMessage, setAnnouncementMessage] = useState('');

  // Voice input state
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [voiceLanguage, setVoiceLanguage] = useState<'en-US' | 'ur-PK'>('en-US');
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const interimTranscriptRef = useRef<string>(''); // Track interim separately

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognitionAPI) {
        setSpeechSupported(true);
        const recognition = new SpeechRecognitionAPI();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = voiceLanguage;

        recognition.onresult = (event: SpeechRecognitionEvent) => {
          let finalTranscript = '';
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          if (finalTranscript) {
            // Final result - set it directly (not append)
            setInputValue(finalTranscript);
            interimTranscriptRef.current = '';
          } else if (interimTranscript) {
            // Show interim results as live feedback
            interimTranscriptRef.current = interimTranscript;
            setInputValue(interimTranscript);
          }
        };

        recognition.onend = () => {
          setIsListening(false);
          console.log('[Voice] Recognition ended');
        };

        recognition.onerror = (event: Event & { error?: string; message?: string }) => {
          setIsListening(false);
          const errorMessage = (event as { error?: string }).error || 'unknown error';
          console.error('[Voice] Recognition error:', errorMessage, event);

          // Provide specific error messages
          let userMessage = 'Voice recognition error. ';
          switch (errorMessage) {
            case 'not-allowed':
              userMessage += 'Microphone permission denied. Please allow microphone access.';
              break;
            case 'no-speech':
              userMessage += 'No speech detected. Please try again.';
              break;
            case 'audio-capture':
              userMessage += 'No microphone found. Please check your microphone.';
              break;
            case 'network':
              userMessage += 'Network error. Please check your connection.';
              break;
            default:
              userMessage += 'Please try again.';
          }
          alert(userMessage); // Show visible error to user
        };

        recognition.onaudiostart = () => {
          console.log('[Voice] Audio capture started');
        };

        recognitionRef.current = recognition;
      } else {
        console.warn('[Voice] Speech Recognition API not supported in this browser');
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [voiceLanguage]);

  // Toggle voice input
  const toggleVoiceInput = useCallback(() => {
    if (!recognitionRef.current) {
      console.error('[Voice] Recognition not initialized');
      alert('Voice recognition not available in this browser');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setInputValue(''); // Clear previous input
      interimTranscriptRef.current = '';

      try {
        recognitionRef.current.start();
        setIsListening(true);
        console.log('[Voice] Started listening in:', voiceLanguage);
      } catch (error) {
        console.error('[Voice] Failed to start:', error);
        // Recognition might already be running, try to restart
        try {
          recognitionRef.current.stop();
          setTimeout(() => {
            recognitionRef.current?.start();
            setIsListening(true);
          }, 100);
        } catch (retryError) {
          console.error('[Voice] Retry failed:', retryError);
          alert('Failed to start voice recognition. Please refresh the page.');
        }
      }
    }
  }, [isListening, voiceLanguage]);

  // Toggle between English and Urdu
  const toggleVoiceLanguage = useCallback(() => {
    const newLang = voiceLanguage === 'en-US' ? 'ur-PK' : 'en-US';
    setVoiceLanguage(newLang);
    if (recognitionRef.current) {
      recognitionRef.current.lang = newLang;
    }
    console.log('[Voice] Language switched to:', newLang);
  }, [voiceLanguage]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Announce messages for screen readers (T068)
  const announceToScreenReader = useCallback((message: string) => {
    setAnnouncementMessage(message);
    // Clear after announcement
    setTimeout(() => setAnnouncementMessage(''), 1000);
  }, []);

  // Global keyboard handler for accessibility (T068)
  useEffect(() => {
    const handleGlobalKeyDown = (e: globalThis.KeyboardEvent) => {
      // Press / to focus input (when not already focused)
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
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

        // Announce to screen reader (T068)
        announceToScreenReader(`Assistant replied: ${assistantMessage.content.substring(0, 100)}`);

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
    <div
      className="flex flex-col h-full min-h-[500px] bg-background rounded-xl border shadow-lg overflow-hidden"
      role="region"
      aria-label="AI Task Assistant chat interface"
    >
      {/* Screen reader announcements (T068) */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {announcementMessage}
      </div>

      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b bg-muted/30">
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary" aria-hidden="true">
          <Bot className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h2 className="font-semibold" id="chat-heading">AI Task Assistant</h2>
          <p className="text-xs text-muted-foreground">Powered by OpenAI</p>
        </div>
      </header>

      {/* Messages */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
        aria-relevant="additions"
        tabIndex={0}
      >
        {messages.map((message) => (
          <article
            key={message.id}
            className={cn(
              'flex gap-3',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
            aria-label={`${message.role === 'user' ? 'You' : 'Assistant'}: ${message.content.substring(0, 50)}${message.content.length > 50 ? '...' : ''}`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center" aria-hidden="true">
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
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center" aria-hidden="true">
                <User className="h-4 w-4 text-secondary-foreground" />
              </div>
            )}
          </article>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start" role="status" aria-label="Assistant is thinking">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center" aria-hidden="true">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Starter Prompts */}
      {messages.length === 1 && (
        <nav className="px-4 pb-2" aria-label="Quick actions">
          <div className="flex flex-wrap gap-2" role="group" aria-label="Suggested prompts">
            {STARTER_PROMPTS.map((prompt, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => handlePromptClick(prompt.prompt)}
                aria-label={`${prompt.label} - click to ${prompt.prompt.endsWith(' ') ? 'start typing' : 'send'}`}
              >
                <span className="mr-1" aria-hidden="true">{prompt.icon}</span>
                {prompt.label}
              </Button>
            ))}
          </div>
        </nav>
      )}

      {/* Input */}
      <footer className="p-4 border-t bg-muted/30">
        <form onSubmit={handleSubmit} className="flex gap-2" aria-label="Message input form">
          <label htmlFor="chat-input" className="sr-only">
            Type a message to the AI assistant
          </label>
          <Input
            id="chat-input"
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={isListening ? `🎤 Listening (${voiceLanguage === 'en-US' ? 'English' : 'اردو'})...` : "Type a message... (Press / to focus)"}
            className={cn("flex-1 bg-background", isListening && "border-red-500 animate-pulse")}
            disabled={isLoading}
            aria-describedby="chat-input-help"
            autoComplete="off"
          />
          <span id="chat-input-help" className="sr-only">
            Press Enter to send, press / from anywhere to focus this input, or click the microphone for voice input
          </span>
          {/* Voice Language Toggle Button */}
          {speechSupported && (
            <Button
              type="button"
              size="icon"
              variant="ghost"
              onClick={toggleVoiceLanguage}
              disabled={isLoading || isListening}
              aria-label={`Switch to ${voiceLanguage === 'en-US' ? 'Urdu' : 'English'}`}
              title={`Language: ${voiceLanguage === 'en-US' ? 'English' : 'اردو'} (click to switch)`}
              className="text-xs font-bold min-w-[40px]"
            >
              {voiceLanguage === 'en-US' ? 'EN' : 'UR'}
            </Button>
          )}
          {/* Voice Input Button */}
          {speechSupported && (
            <Button
              type="button"
              size="icon"
              variant={isListening ? "destructive" : "outline"}
              onClick={toggleVoiceInput}
              disabled={isLoading}
              aria-label={isListening ? "Stop voice input" : `Start voice input (${voiceLanguage === 'en-US' ? 'English' : 'Urdu'})`}
              title={isListening ? "Stop listening" : `Voice command (${voiceLanguage === 'en-US' ? 'English' : 'اردو'})`}
            >
              {isListening ? (
                <MicOff className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Mic className="h-4 w-4" aria-hidden="true" />
              )}
            </Button>
          )}
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !inputValue.trim()}
            aria-label={isLoading ? "Sending message" : "Send message"}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Send className="h-4 w-4" aria-hidden="true" />
            )}
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2 text-center" aria-hidden="true">
          Press <kbd className="px-1 py-0.5 bg-muted rounded text-xs">/</kbd> to focus input
          {speechSupported && ` • 🎤 Voice (${voiceLanguage === 'en-US' ? 'EN' : 'UR'}) • Click EN/UR to switch language`}
        </p>
      </footer>
    </div>
  );
}
