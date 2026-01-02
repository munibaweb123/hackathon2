# Data Model: ChatKit Upgrade to Production Best Practices

## Overview
This document defines the data models required for the ChatKit implementation, extending the existing todo application architecture to support chat interactions, widgets, and conversation history.

## Core Entities

### 1. Thread
Represents a conversation session with unique ID, created/updated timestamps, and associated user.

**Fields**:
- `id` (UUID): Unique identifier for the thread
- `user_id` (UUID): Reference to the user who owns this thread
- `title` (String): Human-readable title for the thread (auto-generated from first message or user-provided)
- `created_at` (DateTime): Timestamp when the thread was created
- `updated_at` (DateTime): Timestamp when the thread was last updated
- `metadata` (JSON): Additional data about the thread (e.g., conversation context, preferences)

**Relationships**:
- One-to-Many: Thread has many Messages
- Many-to-One: Thread belongs to one User

**Validation Rules**:
- `user_id` must reference an existing user
- `created_at` and `updated_at` are automatically managed by the system
- `title` must be between 1-200 characters

### 2. Message
Represents an individual message within a conversation thread.

**Fields**:
- `id` (UUID): Unique identifier for the message
- `thread_id` (UUID): Reference to the thread this message belongs to
- `role` (String): Role of the message sender (user|assistant|system)
- `content` (Text): The text content of the message
- `created_at` (DateTime): Timestamp when the message was created
- `updated_at` (DateTime): Timestamp when the message was last updated
- `metadata` (JSON): Additional data about the message (e.g., widget data, action info)

**Relationships**:
- Many-to-One: Message belongs to one Thread
- One-to-Many: Message may have many Widgets

**Validation Rules**:
- `thread_id` must reference an existing thread
- `role` must be one of: user, assistant, system
- `content` is required for user and system roles

### 3. Widget
JSON structure containing type, id, children, and action definitions that render as interactive UI components.

**Fields**:
- `id` (String): Unique identifier for the widget within the thread
- `message_id` (UUID): Reference to the message this widget is associated with
- `type` (String): Widget type (card, text, button, listview, etc.)
- `payload` (JSON): The actual widget data following ChatKit schema
- `created_at` (DateTime): Timestamp when the widget was created
- `action_handler` (String): Optional reference to the action handler function

**Relationships**:
- Many-to-One: Widget belongs to one Message

**Validation Rules**:
- `message_id` must reference an existing message
- `type` must be a valid ChatKit widget type
- `payload` must follow the ChatKit widget JSON schema

### 4. Action
User interaction event with type, payload, and sender information that triggers backend processing.

**Fields**:
- `id` (UUID): Unique identifier for the action
- `widget_id` (String): Reference to the widget that triggered this action
- `thread_id` (UUID): Reference to the thread where action occurred
- `type` (String): Type of action (button_click, form_submit, etc.)
- `payload` (JSON): Data associated with the action
- `created_at` (DateTime): Timestamp when the action was triggered
- `processed_at` (DateTime): Timestamp when the action was processed
- `result` (JSON): Result of the action processing

**Relationships**:
- Many-to-One: Action belongs to one Thread
- Many-to-One: Action may reference one Widget

**Validation Rules**:
- `thread_id` must reference an existing thread
- `type` must be a valid action type
- `processed_at` is null until action is processed

### 5. User (Extended)
Existing user model with additional fields for ChatKit-specific preferences.

**Fields** (in addition to existing fields):
- `chat_preferences` (JSON): User preferences for chat interactions
- `last_chat_thread_id` (UUID): Reference to the user's most recent chat thread

**Relationships** (in addition to existing):
- One-to-Many: User has many Threads

## State Transitions

### Thread State Transitions
- **Active**: New thread created and ready for messages
- **Archived**: Thread moved to archive after period of inactivity (optional)

### Message State Transitions
- **Draft**: Message created but not yet sent (for user messages)
- **Sent**: Message sent to recipient
- **Read**: Message read by recipient (for assistant messages)

### Widget State Transitions
- **Pending**: Widget created but not yet rendered
- **Rendered**: Widget displayed to user
- **Interacted**: User has interacted with the widget
- **Updated**: Widget has been updated based on user interaction

## Validation Rules Summary

### Thread Validation
- User must exist before creating a thread
- Thread title must be unique per user (within reason)
- Thread must have at least one message to remain active

### Message Validation
- Message must belong to an existing thread
- Only one user message should be pending per thread
- Message content should not exceed reasonable limits (e.g., 10,000 characters)

### Widget Validation
- Widget ID must be unique within the message context
- Widget payload must validate against ChatKit schema
- Widget must be associated with a valid message

### Action Validation
- Action must reference an existing widget or thread
- Action payload must be properly formatted
- Action must not be processed multiple times

## Indexes and Performance Considerations

### Required Indexes
- `threads.user_id`: For efficient user thread retrieval
- `messages.thread_id`: For efficient thread message retrieval
- `messages.created_at`: For chronological message ordering
- `widgets.message_id`: For efficient message widget retrieval
- `actions.thread_id`: For efficient thread action retrieval

### Performance Guidelines
- Implement pagination for threads with many messages (>50 messages)
- Cache frequently accessed widgets to reduce rendering time
- Use database connection pooling for high concurrency
- Implement proper timeout handling for streaming operations

## Migration Strategy

### From Existing Models
- Preserve existing user and task data
- Add new tables for Thread, Message, Widget, and Action
- Update existing authentication to support ChatKit endpoints
- Maintain backward compatibility with existing API endpoints

### Data Migration Steps
1. Create new tables with appropriate constraints
2. Update user table with chat-specific fields
3. Update existing data to reference new relationships if needed
4. Implement migration scripts for any existing conversation data
5. Test migration thoroughly in staging environment

## Security Considerations

### Data Access
- Users can only access their own threads and messages
- Widget data should be sanitized before rendering
- Action payloads should be validated before processing

### Authentication
- All ChatKit endpoints require valid JWT tokens
- Thread access requires token matching thread owner
- Action processing must verify user authorization

### Privacy
- Conversation history should be encrypted at rest
- Sensitive information in messages should be identified and handled appropriately
- Implement data retention policies for chat data