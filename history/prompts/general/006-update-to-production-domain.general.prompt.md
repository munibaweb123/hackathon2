---
id: "006"
title: "Update to Production Domain Configuration"
stage: "general"
date: "2025-12-19"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "update-production-domain"
labels: ["vercel", "production", "domain", "configuration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "backend/.env"
  - "frontend/.env.local"
tests_yaml: []
---

# Update to Production Domain Configuration

## Prompt Text
https://hackathon2-orcin-pi.vercel.app/ use this url

## Response Text
Updated the configuration to use https://hackathon2-orcin-pi.vercel.app as the main production domain:

1. Updated frontend environment variables to use the production domain:
   - NEXT_PUBLIC_BETTER_AUTH_URL set to https://hackathon2-orcin-pi.vercel.app
   - NEXT_PUBLIC_FRONTEND_URL set to https://hackathon2-orcin-pi.vercel.app
   - BETTER_AUTH_URL set to https://hackathon2-orcin-pi.vercel.app

2. Updated backend CORS configuration to focus on the production domain and removed the temporary preview domain

3. Maintained the backend API URL: https://hackathon2-jze5.onrender.com

## Outcome
Configuration updated to use https://hackathon2-orcin-pi.vercel.app as the main production domain for the frontend application, with proper CORS settings and authentication configuration.