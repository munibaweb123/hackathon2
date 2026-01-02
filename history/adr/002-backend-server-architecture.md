# ADR-002: Backend Server Architecture for ChatKit

## Status
Proposed

## Date
2026-01-02

## Context
The ChatKit integration requires a backend server component that can handle user messages and widget interactions. We need to decide on the architectural pattern for implementing the ChatKit server functionality.

## Decision
We will implement the ChatKitServer interface with dedicated respond() and action() methods following OpenAI Agents SDK patterns. This includes:

- A ChatKitServer class with respond() method for handling user input
- An action() method for handling widget interactions (button clicks, form submissions)
- Proper streaming capabilities using ctx.context.stream_widget() for progressive rendering
- Integration with existing FastAPI backend architecture
- Proper CORS configuration for streaming endpoints

## Alternatives Considered
- Direct FastAPI endpoints without ChatKit server interface
- Custom streaming implementation
- WebSocket-based solution
- Server-sent events instead of streaming widgets

## Consequences
### Positive
- Follows official OpenAI ChatKit patterns and best practices
- Enables proper widget streaming and progressive rendering
- Provides clean separation between message handling and action handling
- Integrates well with existing FastAPI architecture
- Supports real-time interactions with widgets

### Negative
- Requires learning and implementing new SDK patterns
- Adds complexity with streaming implementation
- May require additional CORS configuration
- Tight coupling with OpenAI's specific implementation

## References
- specs/001-chatkit-upgrade/plan.md
- specs/001-chatkit-upgrade/research.md
- specs/001-chatkit-upgrade/data-model.md