# ADR-001: ChatKit Integration Architecture

## Status
Proposed

## Date
2026-01-02

## Context
The todo application needs to integrate with OpenAI's ChatKit to provide conversational task management capabilities. We need to decide how to architect the integration between the existing todo application and the new ChatKit functionality while maintaining compatibility with existing architecture patterns.

## Decision
We will implement ChatKit integration using the official OpenAI ChatKit SDK patterns with a dedicated backend server interface and frontend CDN integration. This includes:

- Backend: ChatKitServer interface with respond() and action() methods
- Frontend: Official ChatKit CDN script with React component integration
- Widget streaming: Using ctx.context.stream_widget() pattern from OpenAI Agents SDK
- Authentication: Integration with existing Better Auth JWT system

## Alternatives Considered
- Custom chat implementation without ChatKit SDK
- Third-party chat widget libraries
- Direct OpenAI API integration without ChatKit
- Complete architectural overhaul

## Consequences
### Positive
- Leverages official OpenAI standards and best practices
- Maintains consistency with existing application architecture
- Enables proper widget streaming and progressive rendering
- Integrates with existing authentication system
- Follows production-ready patterns

### Negative
- Adds dependency on external ChatKit CDN
- Increases complexity of the codebase
- Requires additional authentication handling for chat endpoints
- Potential availability issues if ChatKit CDN is down

## References
- specs/001-chatkit-upgrade/plan.md
- specs/001-chatkit-upgrade/research.md
- specs/001-chatkit-upgrade/data-model.md