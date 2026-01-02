# Skill: ai.chatkit.frontend

OpenAI ChatKit frontend integration - production patterns for building AI chatbots.

## Overview

Embed ChatKit UI into Next.js/React frontends with custom backend integration (FastAPI + Agents SDK).

```
Browser → ChatKit React Component → Custom Backend API → Agents SDK → OpenAI
```

## CRITICAL: ChatKit CDN Script Required

**THE MOST COMMON MISTAKE**: Forgetting to load the ChatKit CDN script.

**Without this script, widgets will NOT render with proper styling.**

### Next.js Solution (Required)

```tsx
// src/app/layout.tsx
import Script from "next/script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* CRITICAL: Load ChatKit CDN script for widget styling */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
        {children}
      </body>
    </html>
  );
}
```

### Symptoms if CDN script is missing:
- Widgets render but have no styling
- ChatKit appears blank or broken
- Widget components don't display properly
- No visual feedback when interacting with widgets

**First debugging step**: Always verify the CDN script is loaded.

## Quick Start: HTML Integration

```html
<!-- Add ChatKit script -->
<script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>

<!-- Mount ChatKit -->
<div id="my-chat"></div>

<script>
const chatkit = document.getElementById('my-chat');
chatkit.setOptions({
  api: {
    async getClientSecret(currentClientSecret) {
      if (!currentClientSecret) {
        const res = await fetch('/api/chatkit/session', { method: 'POST' });
        const {client_secret} = await res.json();
        return client_secret;
      }
      // Refresh logic
      const res = await fetch('/api/chatkit/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentClientSecret })
      });
      const {client_secret} = await res.json();
      return client_secret;
    }
  }
});
</script>
```

## This Project: Custom Backend Mode

This project uses **custom backend mode** - ChatKit talks to our FastAPI backend instead of OpenAI directly.

```
Frontend (ChatKit) → /api/chatkit → FastAPI → Agents SDK → OpenAI
```

## ChatKit React Component Setup

### Install Dependencies

```bash
npm install @openai/chatkit-react
```

### Basic Chat Component

```tsx
// components/chat/chat-widget.tsx
'use client';

import { useChatKit, ChatKit } from '@openai/chatkit-react';
import { getJwtToken } from '@/lib/auth-client';

export function ChatWidget() {
  const chatkit = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL}/api/chatkit`,
      fetch: async (url, init) => {
        // Get JWT token for authentication
        const token = await getJwtToken();
        return fetch(url, {
          ...init,
          headers: {
            ...init?.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      },
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'default',
    },
    onError: ({ error }) => {
      console.error('[ChatKit] Error:', error);
    },
  });

  return (
    <div className="h-full w-full">
      <ChatKit control={chatkit.control} />
    </div>
  );
}
```

### Chat Page with Auth Protection

```tsx
// app/(dashboard)/chat/page.tsx
'use client';

import { useAuth } from '@/hooks/use-auth';
import { ChatWidget } from '@/components/chat/chat-widget';
import { Loader2 } from 'lucide-react';

export default function ChatPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-full">
        <p>Please sign in to use the chat.</p>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-4rem)]">
      <ChatWidget />
    </div>
  );
}
```

---

## Theme Customization

### Basic Theming

```javascript
chatkit.setOptions({
  theme: {
    // Primary brand color
    primaryColor: '#0066FF',

    // Typography
    fontFamily: 'Inter, -apple-system, sans-serif',
    fontSize: '14px',

    // Background colors
    backgroundColor: '#FFFFFF',
    messageBackgroundColor: '#F5F5F5',

    // Border radius
    borderRadius: '8px',

    // Shadows
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  }
});
```

### Dark Mode Support

```javascript
const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

chatkit.setOptions({
  theme: {
    primaryColor: isDarkMode ? '#4A9EFF' : '#0066FF',
    backgroundColor: isDarkMode ? '#1A1A1A' : '#FFFFFF',
    textColor: isDarkMode ? '#FFFFFF' : '#000000',
    messageBackgroundColor: isDarkMode ? '#2A2A2A' : '#F5F5F5'
  }
});
```

### Custom CSS

```css
/* Override ChatKit styles */
#my-chat {
  --chatkit-primary: #0066FF;
  --chatkit-bg: #FFFFFF;
  --chatkit-text: #000000;
}

/* Customize message bubbles */
#my-chat .message-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 18px;
}

/* Customize input area */
#my-chat .input-container {
  border-top: 2px solid #E0E0E0;
  padding: 16px;
}
```

## Brand Integration

### Logo and Welcome Message

```javascript
chatkit.setOptions({
  branding: {
    logo: 'https://yoursite.com/logo.svg',
    companyName: 'Your Company',
    welcomeMessage: 'Hi! How can I help you today?',
    placeholder: 'Type your message...'
  }
});
```

### Custom Avatar

```javascript
chatkit.setOptions({
  avatar: {
    bot: 'https://yoursite.com/bot-avatar.png',
    user: 'https://yoursite.com/user-avatar.png'
  }
});
```

## Behavior Customization

### Auto-open Configuration

```javascript
chatkit.setOptions({
  autoOpen: true,  // Open chat on page load
  minimized: false,  // Start expanded
  showOnMobile: true  // Show on mobile devices
});
```

### Message Handling

```javascript
chatkit.setOptions({
  onMessage: (message) => {
    console.log('New message:', message);
    // Track analytics
    analytics.track('Chat Message', {
      content: message.text,
      timestamp: message.timestamp
    });
  },

  onError: (error) => {
    console.error('Chat error:', error);
    // Report to error tracking
    errorTracker.report(error);
  }
});
```

### Rate Limiting

```javascript
chatkit.setOptions({
  rateLimit: {
    maxMessagesPerMinute: 10,
    messageOnLimit: "You're sending messages too quickly. Please wait a moment."
  }
});
```

## Responsive Design

### Mobile Optimization

```javascript
chatkit.setOptions({
  responsive: {
    breakpoint: 768,  // Switch to mobile layout below 768px
    mobileHeight: '100vh',
    desktopHeight: '600px',
    mobilePosition: 'fixed',  // Full screen on mobile
    desktopPosition: 'bottom-right'  // Corner widget on desktop
  }
});
```

### Custom Layout

```javascript
chatkit.setOptions({
  layout: {
    width: '400px',
    height: '600px',
    position: 'bottom-right',
    margin: '20px'
  }
});
```

## Internationalization

### Multi-language Support

```javascript
const locale = navigator.language.startsWith('es') ? 'es' : 'en';

chatkit.setOptions({
  locale: locale,
  translations: {
    es: {
      welcomeMessage: 'Hola! Como puedo ayudarte?',
      placeholder: 'Escribe tu mensaje...',
      sendButton: 'Enviar'
    },
    en: {
      welcomeMessage: 'Hi! How can I help you?',
      placeholder: 'Type your message...',
      sendButton: 'Send'
    }
  }
});
```

## Advanced Configuration

### With File Uploads

```tsx
const chatkit = useChatKit({
  api: {
    url: `${process.env.NEXT_PUBLIC_API_URL}/api/chatkit`,
    fetch: async (url, init) => {
      const token = await getJwtToken();
      return fetch(url, {
        ...init,
        headers: {
          ...init?.headers,
          'Authorization': `Bearer ${token}`,
        },
      });
    },
    uploadStrategy: {
      type: 'direct',
      uploadUrl: `${process.env.NEXT_PUBLIC_API_URL}/api/chatkit/upload`,
    },
    domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY,
  },
  onError: ({ error }) => {
    console.error('[ChatKit] Error:', error);
  },
});
```

### With Custom Actions

```tsx
const chatkit = useChatKit({
  api: {
    url: `${process.env.NEXT_PUBLIC_API_URL}/api/chatkit`,
    fetch: customFetch,
    domainKey: 'your-domain-key',
  },
  actions: {
    // Custom action when user clicks a task in the widget
    onTaskClick: (taskId: number) => {
      console.log('Task clicked:', taskId);
      // Navigate to task detail page
      router.push(`/tasks/${taskId}`);
    },
    // Custom action for completing tasks from widget
    onTaskComplete: async (taskId: number) => {
      await completeTask(taskId);
      // Refresh the chat to show updated widget
      chatkit.control.refresh();
    },
  },
  onError: ({ error }) => {
    console.error('[ChatKit] Error:', error);
  },
});
```

### Passing User Context to Backend

```tsx
const chatkit = useChatKit({
  api: {
    url: `${process.env.NEXT_PUBLIC_API_URL}/api/chatkit`,
    fetch: async (url, init) => {
      const token = await getJwtToken();

      // Parse and modify request body to add user context
      let body = init?.body;
      if (body && typeof body === 'string') {
        const parsed = JSON.parse(body);
        parsed.context = {
          user_id: user?.id,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        };
        body = JSON.stringify(parsed);
      }

      return fetch(url, {
        ...init,
        body,
        headers: {
          ...init?.headers,
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    },
    domainKey: 'your-domain-key',
  },
});
```

## Analytics Integration

### Track Conversations

```javascript
chatkit.setOptions({
  analytics: {
    onConversationStart: (conversationId) => {
      analytics.track('Conversation Started', { conversationId });
    },
    onConversationEnd: (conversationId, messageCount) => {
      analytics.track('Conversation Ended', {
        conversationId,
        messageCount
      });
    },
    onUserSatisfaction: (rating, conversationId) => {
      analytics.track('User Satisfaction', {
        rating,
        conversationId
      });
    }
  }
});
```

## Performance Optimization

### Lazy Loading

```javascript
// Load ChatKit only when needed
document.getElementById('chat-trigger').addEventListener('click', () => {
  const script = document.createElement('script');
  script.src = 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js';
  script.async = true;
  document.head.appendChild(script);
});
```

### Resource Preloading

```html
<!-- Preload ChatKit resources -->
<link rel="preload" href="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" as="script">
<link rel="preload" href="https://cdn.platform.openai.com/deployments/chatkit/chatkit.css" as="style">
```

## Environment Variables

```env
# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Debugging Common Issues

### 1. Blank/Empty Widget

**Check in order:**
1. Is CDN script loaded? Check Network tab for `chatkit.js`
2. Is the component mounted? Add console.log in component
3. Are there console errors? Check browser console
4. Is the API endpoint reachable? Check Network tab

```tsx
// Debug wrapper
export function ChatWidgetDebug() {
  useEffect(() => {
    console.log('[ChatKit] Component mounted');
    console.log('[ChatKit] API URL:', process.env.NEXT_PUBLIC_API_URL);
  }, []);

  return <ChatWidget />;
}
```

### 2. Authentication Errors (401)

```tsx
// Check token is being sent
const chatkit = useChatKit({
  api: {
    url: apiUrl,
    fetch: async (url, init) => {
      const token = await getJwtToken();
      console.log('[ChatKit] Token present:', !!token);
      console.log('[ChatKit] Token preview:', token?.substring(0, 20) + '...');

      return fetch(url, {
        ...init,
        headers: {
          ...init?.headers,
          'Authorization': `Bearer ${token}`,
        },
      });
    },
  },
});
```

### 3. CORS Errors

Ensure FastAPI backend has proper CORS configuration:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Widgets Not Rendering Properly

Check that widgets are being streamed correctly from the backend:

```tsx
// Add response logging
const chatkit = useChatKit({
  api: {
    url: apiUrl,
    fetch: async (url, init) => {
      const response = await fetch(url, { ...init });

      // Clone and log response for debugging
      const cloned = response.clone();
      const text = await cloned.text();
      console.log('[ChatKit] Response:', text);

      return response;
    },
  },
});
```

## Use Case Examples

### Customer Support

```javascript
chatkit.setOptions({
  theme: { primaryColor: '#4CAF50' },
  branding: {
    welcomeMessage: 'Need help? Ask me anything!',
    logo: '/support-logo.svg'
  },
  features: {
    fileUpload: true,
    feedbackEnabled: true,
    escalationToHuman: true
  }
});
```

### Sales/Lead Generation

```javascript
chatkit.setOptions({
  theme: { primaryColor: '#FF6B35' },
  branding: {
    welcomeMessage: 'Looking for our products? Let me help!',
  },
  onLeadCaptured: (leadData) => {
    // Send to CRM
    crm.createLead(leadData);
  }
});
```

### Internal Knowledge Base

```javascript
chatkit.setOptions({
  theme: { primaryColor: '#6C63FF' },
  auth: {
    required: true,
    provider: 'oauth'
  },
  features: {
    searchEnabled: true,
    documentUpload: true
  }
});
```

## Custom Chat UI (Without ChatKit Component)

If you need full control over the UI:

```tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { jwtApiClient } from '@/services/auth/api-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  widgets?: any[];
}

export function CustomChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call your custom chat endpoint
      const response = await jwtApiClient.post('/api/chat', {
        message: input,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        widgets: response.data.widgets,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted p-3 rounded-lg">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message..."
            className="flex-1 p-2 border rounded-lg"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Security Best Practices

1. **Never store API keys in frontend** - Use backend proxy
2. **Always use HTTPS in production**
3. **Validate tokens on backend** - Don't trust frontend auth
4. **Use environment variables** - Never hardcode secrets
5. **Implement rate limiting** - Protect against abuse

## Deployment Checklist

- [ ] CDN script loaded in layout
- [ ] API URL configured correctly
- [ ] Domain key set in environment
- [ ] Auth token passed in requests
- [ ] CORS configured on backend
- [ ] HTTPS enabled in production
- [ ] Error handling implemented
- [ ] Analytics tracking set up

## File Locations

- Chat widget: `frontend/src/components/chat/chat-widget.tsx`
- Chat page: `frontend/src/app/(dashboard)/chat/page.tsx`
- Auth client: `frontend/src/lib/auth-client.ts`
- API client: `frontend/src/services/auth/api-client.ts`

## Related Skills

- `ai.chatkit.backend` - Backend ChatKit server implementation
- `auth.frontend` - Client-side authentication
- `auth.hook` - useAuth hook for auth state
