# ADR-003: Data Model for ChatKit Conversations

## Status
Proposed

## Date
2026-01-02

## Context
The ChatKit implementation requires new data models to store conversation threads, messages, widgets, and user interactions. We need to design these models to work with existing database infrastructure while supporting ChatKit-specific features.

## Decision
We will extend the existing data model with new entities for conversation management:

- Thread: Represents a conversation session with user association and metadata
- Message: Individual messages within threads with role-based differentiation
- Widget: JSON-based UI components with type, payload, and action definitions
- Action: User interactions with widgets that trigger backend processing
- Extended User model: With chat preferences and last thread reference

These entities will maintain compatibility with existing SQLModel patterns and database infrastructure.

## Alternatives Considered
- Separate data model for chat interactions
- Complete data model overhaul
- External data storage for chat data
- In-memory only storage without persistence

## Consequences
### Positive
- Maintains consistency with existing data architecture
- Supports conversation history and persistence across sessions
- Enables complex widget interactions with proper state tracking
- Integrates with existing authentication and user management
- Supports proper indexing and performance optimization

### Negative
- Increases database schema complexity
- Requires additional migration steps
- May impact performance with large conversation histories
- Adds complexity to data validation and relationships

## References
- specs/001-chatkit-upgrade/plan.md
- specs/001-chatkit-upgrade/research.md
- specs/001-chatkit-upgrade/data-model.md