# ADR-004: Authentication Integration for ChatKit

## Status
Proposed

## Date
2026-01-02

## Context
The ChatKit endpoints need to integrate with the existing authentication system to ensure only authorized users can access their conversations and perform actions. We need to decide how to handle authentication for the new ChatKit functionality.

## Decision
We will integrate ChatKit with the existing Better Auth JWT authentication system. This includes:

- All ChatKit endpoints require valid JWT tokens from Better Auth
- Thread access is restricted to the owning user based on token
- Action processing verifies user authorization before execution
- Proper CORS headers for authentication with ChatKit CDN
- Consistent authentication patterns with existing API endpoints

## Alternatives Considered
- Separate authentication system for ChatKit
- No authentication (insecure)
- Session-based authentication instead of JWT
- OAuth integration for ChatKit specifically

## Consequences
### Positive
- Maintains consistency with existing security architecture
- Leverages proven authentication infrastructure
- Ensures proper user isolation and data privacy
- Reduces complexity by reusing existing auth patterns
- Maintains security best practices

### Negative
- May add complexity to ChatKit request handling
- Requires careful token validation in streaming contexts
- Potential performance impact from additional auth checks
- Need to handle authentication errors gracefully in chat interface

## References
- specs/001-chatkit-upgrade/plan.md
- specs/001-chatkit-upgrade/research.md
- specs/001-chatkit-upgrade/data-model.md