---
id: 3
title: Fix WebSocket imports after authentication update
stage: general
date_iso: 2026-01-28
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 004-advanced-cloud-deploy
user: Claude
command: "fix websocket imports"
labels: ["bugfix", "websocket", "imports", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - backend/app/api/websocket.py
tests_yaml: []
prompt_text: |
  After updating the WebSocket authentication to handle query parameter tokens,
  the server failed to start due to missing imports. The Depends and get_current_user
  imports were inadvertently removed when updating the WebSocket endpoint.
response_text: |
  Fixed the missing imports in the WebSocket API file. Added back the Depends
  and get_current_user imports that were needed for the /status endpoint.
outcome: |
  WebSocket API now imports all required dependencies and should start successfully.
evaluation: |
  The fix resolves the import error that was preventing the server from starting.
---

# Fix WebSocket Import Error

## Summary

Fixed missing imports in the WebSocket API file that occurred when updating the authentication mechanism.

## Changes Made

1. Added back the `Depends` import to the WebSocket API file
2. Added back the `get_current_user` import to support the /status endpoint

## Files Modified

- `backend/app/api/websocket.py` - Restored missing imports