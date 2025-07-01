# 01-2: Chat Frontend UI - React Interface with Streaming

## Objective
Build a modern, responsive chat interface in React that connects to the FastAPI backend, supports real-time streaming, and provides an enhanced user experience compared to the original Streamlit interface.

## Prerequisites
- Chat API backend completed (01-1)
- Frontend foundation setup (00-3)
- Backend streaming endpoints functional

## Implementation Steps

### 1. Chat Component Architecture
- Design component hierarchy for chat interface
- Create reusable message components
- Implement chat input with enhanced features
- Build message list with virtualization for performance
- Create typing indicators and status displays

### 2. Real-time Integration
- Implement WebSocket connection management
- Create hooks for real-time message streaming
- Add connection state handling and reconnection logic
- Implement optimistic updates for better UX
- Handle connection errors and fallbacks

### 3. Message Management
- Create message state management with Zustand
- Implement message history loading and pagination
- Add message search and filtering capabilities
- Create conversation management (create, delete, rename)
- Implement message persistence and sync

### 4. Enhanced Chat Features
- Add file attachment support for documents
- Implement markdown rendering for code blocks
- Create syntax highlighting for code snippets
- Add message reactions and bookmarking
- Implement conversation export functionality

### 5. UI/UX Enhancements
- Create responsive design for mobile and desktop
- Implement smooth scrolling and auto-scroll
- Add keyboard shortcuts and accessibility
- Create loading states and error handling
- Implement dark/light theme support

## Files to Create

### Core Chat Components
1. `frontend/src/components/chat/ChatInterface.tsx` - Main chat container
2. `frontend/src/components/chat/MessageList.tsx` - Virtualized message list
3. `frontend/src/components/chat/MessageBubble.tsx` - Individual message component
4. `frontend/src/components/chat/MessageInput.tsx` - Enhanced input with features
5. `frontend/src/components/chat/ConversationSidebar.tsx` - Conversation list
6. `frontend/src/components/chat/TypingIndicator.tsx` - Real-time typing indicator

### Advanced Features
7. `frontend/src/components/chat/MessageReactions.tsx` - Message reactions UI
8. `frontend/src/components/chat/CodeBlock.tsx` - Code syntax highlighting
9. `frontend/src/components/chat/FileAttachment.tsx` - File upload component
10. `frontend/src/components/chat/ConversationHeader.tsx` - Chat header with actions
11. `frontend/src/components/chat/MessageSearch.tsx` - Search functionality
12. `frontend/src/components/chat/ExportDialog.tsx` - Export conversation

### Hooks and Services
13. `frontend/src/hooks/useChat.ts` - Chat state and operations
14. `frontend/src/hooks/useWebSocket.ts` - WebSocket connection management
15. `frontend/src/hooks/useMessageStream.ts` - Streaming message handling
16. `frontend/src/hooks/useConversations.ts` - Conversation management
17. `frontend/src/services/chatService.ts` - Chat API integration
18. `frontend/src/services/websocketService.ts` - WebSocket service

### State Management
19. `frontend/src/store/chatStore.ts` - Chat state store
20. `frontend/src/store/conversationStore.ts` - Conversation state
21. `frontend/src/types/chat.ts` - Chat type definitions

### Utilities
22. `frontend/src/utils/messageFormatter.ts` - Message formatting utilities
23. `frontend/src/utils/markdown.ts` - Markdown rendering utilities
24. `frontend/src/utils/scrollUtils.ts` - Scroll management utilities

## Key Components Implementation

### 1. Chat Interface Container
```tsx
// frontend/src/components/chat/ChatInterface.tsx
import React, { useEffect, useRef } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ConversationSidebar } from './ConversationSidebar';
import { useChat } from '@/hooks/useChat';

export const ChatInterface: React.FC = () => {
  const {
    currentConversation,
    messages,
    isLoading,
    sendMessage,
    loadConversation
  } = useChat();

  return (
    <div className="flex h-full bg-background">
      <ConversationSidebar />
      <div className="flex-1 flex flex-col">
        <ConversationHeader />
        <MessageList 
          messages={messages}
          isLoading={isLoading}
        />
        <MessageInput 
          onSendMessage={sendMessage}
          disabled={isLoading}
        />
      </div>
    </div>
  );
};
```

### 2. Enhanced Message Bubble
```tsx
// frontend/src/components/chat/MessageBubble.tsx
import React from 'react';
import { Message } from '@/types/chat';
import { CodeBlock } from './CodeBlock';
import { cn } from '@/utils/cn';

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isStreaming = false
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div className={cn(
      'flex mb-4',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'max-w-[80%] rounded-lg px-4 py-2',
        isUser 
          ? 'bg-primary text-primary-foreground' 
          : 'bg-muted text-foreground'
      )}>
        <MessageContent 
          content={message.content}
          isStreaming={isStreaming}
        />
        <MessageMetadata 
          timestamp={message.timestamp}
          isStreaming={isStreaming}
        />
      </div>
    </div>
  );
};
```

### 3. Real-time WebSocket Hook
```tsx
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { useChat } from './useChat';

export const useWebSocket = (conversationId: string) => {
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const ws = useRef<WebSocket | null>(null);
  const { addMessage, updateStreamingMessage } = useChat();

  useEffect(() => {
    if (!conversationId) return;

    const connectWebSocket = () => {
      setConnectionState('connecting');
      ws.current = new WebSocket(`ws://localhost:8000/api/ws/chat/${conversationId}`);

      ws.current.onopen = () => {
        setConnectionState('connected');
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
          updateStreamingMessage(data.content);
        } else if (data.type === 'complete') {
          addMessage(data.message);
        }
      };

      ws.current.onclose = () => {
        setConnectionState('disconnected');
        // Implement reconnection logic
        setTimeout(connectWebSocket, 1000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionState('disconnected');
      };
    };

    connectWebSocket();

    return () => {
      ws.current?.close();
    };
  }, [conversationId]);

  const sendMessage = (message: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ content: message }));
    }
  };

  return { connectionState, sendMessage };
};
```

### 4. Chat State Store
```tsx
// frontend/src/store/chatStore.ts
import { create } from 'zustand';
import { Message, Conversation } from '@/types/chat';

interface ChatState {
  currentConversation: Conversation | null;
  conversations: Conversation[];
  messages: Message[];
  isLoading: boolean;
  streamingMessage: string;
  
  // Actions
  setCurrentConversation: (conversation: Conversation) => void;
  addMessage: (message: Message) => void;
  updateStreamingMessage: (chunk: string) => void;
  clearStreamingMessage: () => void;
  loadConversations: () => Promise<void>;
  createConversation: () => Promise<Conversation>;
  deleteConversation: (id: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  currentConversation: null,
  conversations: [],
  messages: [],
  isLoading: false,
  streamingMessage: '',

  setCurrentConversation: (conversation) => {
    set({ currentConversation: conversation });
    // Load messages for this conversation
  },

  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message],
      streamingMessage: ''
    }));
  },

  updateStreamingMessage: (chunk) => {
    set((state) => ({
      streamingMessage: state.streamingMessage + chunk
    }));
  },

  clearStreamingMessage: () => {
    set({ streamingMessage: '' });
  },

  loadConversations: async () => {
    set({ isLoading: true });
    try {
      // API call to load conversations
      const conversations = await chatService.getConversations();
      set({ conversations, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      // Handle error
    }
  },

  createConversation: async () => {
    const conversation = await chatService.createConversation();
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      currentConversation: conversation
    }));
    return conversation;
  },

  deleteConversation: async (id) => {
    await chatService.deleteConversation(id);
    set((state) => ({
      conversations: state.conversations.filter(c => c.id !== id),
      currentConversation: state.currentConversation?.id === id ? null : state.currentConversation
    }));
  }
}));
```

### 5. Enhanced Message Input
```tsx
// frontend/src/components/chat/MessageInput.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Send, Paperclip, Mic } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string, attachments?: File[]) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message..."
}) => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim(), attachments);
      setMessage('');
      setAttachments([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t bg-background">
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className="min-h-[40px] max-h-[200px] resize-none"
            rows={1}
          />
          {attachments.length > 0 && (
            <AttachmentPreview 
              attachments={attachments}
              onRemove={(index) => setAttachments(prev => prev.filter((_, i) => i !== index))}
            />
          )}
        </div>
        
        <div className="flex space-x-1">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => {/* Handle file attachment */}}
            disabled={disabled}
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          
          <Button
            type="submit"
            size="sm"
            disabled={disabled || !message.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </form>
  );
};
```

## Advanced Features Implementation

### 1. Message Virtualization
- Implement react-window for large message lists
- Add smooth scrolling with auto-scroll to bottom
- Implement infinite scroll for message history

### 2. Markdown and Code Support
- Integrate react-markdown for rich text rendering
- Add syntax highlighting with prism-react-renderer
- Support for mathematical expressions with KaTeX

### 3. File Attachment System
- Implement drag-and-drop file upload
- Add file type validation and size limits
- Create file preview components
- Support for image, PDF, and document uploads

## Success Criteria
- [ ] Chat interface renders and is responsive
- [ ] Real-time messaging works via WebSocket
- [ ] Message streaming displays smoothly
- [ ] Conversation management (create, delete, switch) functions
- [ ] File attachments can be uploaded and displayed
- [ ] Markdown and code blocks render correctly
- [ ] Keyboard shortcuts work (Enter to send, etc.)
- [ ] Dark/light theme toggle affects chat interface
- [ ] Mobile responsive design works properly
- [ ] Error states and loading indicators display correctly
- [ ] Message search and filtering work
- [ ] Conversation export functionality works

## Performance Considerations
- Implement message virtualization for large conversations
- Use React.memo and useMemo for expensive operations
- Optimize WebSocket reconnection logic
- Implement proper cleanup for WebSocket connections
- Add debouncing for search and typing indicators

## Accessibility
- Proper ARIA labels for screen readers
- Keyboard navigation support
- Focus management for message input
- Color contrast compliance
- Screen reader announcements for new messages

## Estimated Time
8-10 hours

## Next Steps
After completion, proceed to `02-1-plan-document-api-backend.md`