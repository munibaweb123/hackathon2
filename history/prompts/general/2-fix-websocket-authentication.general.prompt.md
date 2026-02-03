---
id: 2
title: Fix WebSocket authentication for query parameter token
stage: general
date_iso: 2026-01-28
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 004-advanced-cloud-deploy
user: Claude
command: "fix websocket authentication"
labels: ["bugfix", "websocket", "authentication", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - backend/app/api/websocket.py
tests_yaml: []
prompt_text: |
  ## Error Type
  Console Error

  ## Error Message
  [WS] Error: {}

      at createConsoleError (file:///mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/frontend/.next/dev/static/chunks/node_modules_next_dist_7a8122d0._.js:2189:71)
      at handleConsoleError (file:///mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/frontend/.next/dev/static/chunks/node_modules_next_dist_7a8122d0._.js:2970:54)
      at console.error (file:///mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/frontend/.next/dev/static/chunks/node_modules_next_dist_7a8122d0._.js:3114:57)
      at ws.onerror (file:///mnt/c/Users/YOusuf Traders/Documents/quarter-4/hackathon_2/frontend/.next/dev/static/chunks/src_452bd5f8._.js:3750:25)

  Next.js version: 16.0.8 (Turbopack)
response_text: |
  Fixed the WebSocket authentication by updating the WebSocket endpoint to properly
  handle JWT tokens passed as query parameters instead of Authorization headers.
  WebSocket connections now authenticate correctly by extracting the token from
  the query string and validating it using the decode_jwt_token function.
outcome: |
  WebSocket connections now properly authenticate using tokens passed as query parameters.
evaluation: |
  The fix resolves the authentication issue that was causing WebSocket connection failures.
---

# Fix WebSocket Authentication Issue

## Summary

Fixed the WebSocket authentication issue where JWT tokens were expected in Authorization headers but were being passed as query parameters.

## Changes Made

1. Updated the WebSocket endpoint in `backend/app/api/websocket.py` to accept token as a query parameter
2. Modified the authentication logic to use `decode_jwt_token` function to validate the token from the query string
3. Added proper error handling for invalid tokens

## Files Modified

- `backend/app/api/websocket.py` - Updated WebSocket endpoint to handle query parameter authentication