---
id: "001"
title: "Fix CORS Error"
stage: "general"
date: "2025-12-19"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "main"
user: "user"
command: "fix-cors-error"
labels: ["cors", "authentication", "frontend", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "backend/.env"
tests_yaml: []
---

# Fix CORS Error

## Prompt Text
Access to fetch at 'http://localhost:3000/api/auth/get-session' from origin 'https://hackathon2-9l6evr5v8-munibas-projects-467ff0a3.vercel.app' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.

## Response Text
I've identified and fixed the CORS issue in your application:

### Problem
The CORS (Cross-Origin Resource Sharing) error occurred because:
1. Your frontend is deployed on Vercel (`https://hackathon2-9l6evr5v8-munibas-projects-467ff0a3.vercel.app`)
2. Your backend only allowed requests from `http://localhost:3000` and `http://127.0.0.1:3000`
3. The browser blocked cross-origin requests due to this mismatch

### Solution
I've updated the backend configuration in `backend/.env`:

1. **Updated CORS_ORIGINS**: Added your Vercel domain to the allowed origins list:
   ```
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://hackathon2-9l6evr5v8-munibas-projects-467ff0a3.vercel.app
   ```

2. **Updated BETTER_AUTH_URL**: Changed from localhost to your Vercel domain to ensure proper communication between backend and frontend auth services:
   ```
   BETTER_AUTH_URL=https://hackathon2-9l6evr5v8-munibas-projects-467ff0a3.vercel.app
   ```

### Next Steps
To fully resolve the issue, you'll need to:
1. **Restart your backend server** to pick up the new environment variables
2. **Ensure your backend is accessible from the internet** - if your backend is running locally, it won't be able to communicate with the Vercel frontend. You'll need to either:
   - Deploy your backend to a cloud platform (like Render, Railway, or AWS)
   - Use a tunneling service like ngrok to expose your local backend
   - Run the backend locally but make sure it has internet access to reach the Vercel domain

After these changes and ensuring your backend is accessible, the CORS error should be resolved and authentication should work properly between your Vercel frontend and backend server.

## Outcome
Successfully identified and fixed the CORS configuration issue by updating the environment variables in the backend. The frontend domain was added to the allowed CORS origins and the Better Auth URL was updated to point to the deployed frontend.