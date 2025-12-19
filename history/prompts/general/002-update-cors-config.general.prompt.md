---
id: "002"
title: "Update CORS Configuration with Correct Vercel Domain"
stage: "general"
date: "2025-12-19"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "update-cors-config"
labels: ["cors", "authentication", "frontend", "backend", "vercel"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "backend/.env"
tests_yaml: []
---

# Update CORS Configuration with Correct Vercel Domain

## Prompt Text
login:1 Access to fetch at 'http://localhost:3000/api/auth/get-session' from origin 'https://hackathon2-ecxpwekmx-munibas-projects-467ff0a3.vercel.app' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.

## Response Text
I've updated the CORS configuration to use the correct Vercel domain provided by the user. The previous domain I used was incorrect, and I've now updated both the CORS_ORIGINS and BETTER_AUTH_URL settings in the backend configuration to use the correct domain: https://hackathon2-orcin-pi.vercel.app

## Changes Made
1. Updated CORS_ORIGINS in backend/.env to include the correct Vercel domain
2. Updated BETTER_AUTH_URL in backend/.env to point to the correct Vercel domain

## Outcome
The CORS configuration now includes the correct Vercel domain, which should resolve the cross-origin resource sharing errors when the frontend tries to access backend API endpoints.