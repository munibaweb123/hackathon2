# Quickstart: Enhanced Authentication Implementation

## Overview
This guide provides step-by-step instructions to implement the enhanced authentication system in the todo web application using Better Auth.

## Prerequisites
- Node.js 18+ (for frontend)
- Python 3.13+ (for backend)
- FastAPI installed in backend
- Next.js 14+ with App Router (for frontend)

## Backend Setup (FastAPI)

### 1. Install Dependencies
```bash
# In backend directory
pip install python-jose[cryptography] pyjwt bcrypt python-multipart
```

### 2. Update Requirements
Add to `requirements.txt`:
```
python-jose[cryptography]
pyjwt
bcrypt
python-multipart
```

### 3. Create User Model
Update `backend/app/models/user.py` with the fields defined in the data model.

### 4. Create Authentication Schemas
Create `backend/app/schemas/auth.py`:
- User registration schema
- User login schema
- Token schema
- User response schema

### 5. Update Authentication Logic
Enhance `backend/app/core/auth.py` with:
- Password hashing functions
- JWT creation and verification
- Token refresh logic
- User authentication utilities

### 6. Create Auth Endpoints
Create `backend/app/api/auth/` with endpoints matching the API contracts:
- `/register`
- `/login`
- `/logout`
- `/me`
- `/refresh`
- `/forgot-password`
- `/reset-password`

### 7. Protect Existing Endpoints
Update existing API endpoints (tasks, preferences, reminders) to require authentication using JWT middleware.

## Frontend Setup (Next.js)

### 1. Install Better Auth
```bash
# In frontend directory
npm install better-auth
```

### 2. Initialize Better Auth Client
Create authentication configuration following the auth.betterAuth.md skill.

### 3. Create Authentication Pages
Create pages in `todo_web_frontend/src/app/`:
- `(auth)/login/page.tsx`
- `(auth)/register/page.tsx`
- `(auth)/forgot-password/page.tsx`
- `(auth)/reset-password/page.tsx`

### 4. Update Layout for Protected Routes
Modify `(dashboard)/layout.tsx` to protect routes that require authentication.

### 5. Create Authentication Hook
Enhance `use-auth.ts` hook to work with Better Auth and manage user state.

### 6. Create Authentication Components
Create components in `todo_web_frontend/src/components/auth/`:
- LoginForm
- RegisterForm
- ForgotPasswordForm

### 7. Update API Service
Enhance `api-service.ts` to include authentication headers for protected endpoints.

## Integration Steps

### 1. Connect Frontend and Backend
- Configure JWT handling between Better Auth and FastAPI backend
- Ensure user data is synchronized between systems
- Set up proper session management

### 2. Update Existing Components
- Modify existing task, preference, and reminder components to work with authenticated user data
- Update data fetching to include authentication tokens

### 3. Implement Error Handling
- Handle authentication errors gracefully
- Redirect unauthenticated users to login
- Implement proper logout on token expiration

## Testing
1. Test user registration flow
2. Test user login and session management
3. Test password reset functionality
4. Verify all existing features still work with authentication
5. Test route protection

## Security Considerations
- Store JWTs securely (preferably in HTTP-only cookies)
- Implement proper CSRF protection
- Use HTTPS in production
- Validate all inputs on both frontend and backend
- Implement rate limiting for authentication endpoints