# Data Model: Enhanced Authentication System

## User Entity
**Description**: Represents a registered user in the system

**Fields**:
- `id` (string/UUID): Unique identifier for the user
- `email` (string): User's email address (unique, required, validated)
- `username` (string): User's chosen username (optional, unique if provided)
- `password_hash` (string): Bcrypt/scrypt/Argon2 hash of user's password
- `first_name` (string, optional): User's first name
- `last_name` (string, optional): User's last name
- `is_active` (boolean): Whether the account is active (default: true)
- `is_verified` (boolean): Whether the email is verified (default: false)
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last update timestamp
- `last_login_at` (datetime, optional): Last login timestamp
- `password_reset_token` (string, optional): Token for password reset
- `password_reset_expires` (datetime, optional): When reset token expires
- `verification_token` (string, optional): Token for email verification
- `verification_expires` (datetime, optional): When verification token expires

**Validation Rules**:
- Email must be valid email format
- Email must be unique
- Password must meet strength requirements (min 8 chars, mixed case, numbers, special chars)
- Username if provided must be 3-30 chars, alphanumeric + underscores/hyphens

## Session Entity
**Description**: Represents an active user session

**Fields**:
- `id` (string/UUID): Unique session identifier
- `user_id` (string): Reference to the user
- `token` (string): Session token (JWT or other format)
- `expires_at` (datetime): When the session expires
- `created_at` (datetime): Session creation timestamp
- `last_accessed_at` (datetime): Last time session was used
- `user_agent` (string, optional): Browser/device information
- `ip_address` (string, optional): IP address of session origin

## Authentication Token Entity
**Description**: Represents a secure token used for stateless authentication (JWT)

**Fields**:
- `token` (string): The JWT token string
- `user_id` (string): Reference to the user
- `expires_at` (datetime): When the token expires
- `created_at` (datetime): Token creation timestamp
- `type` (string): Token type (access, refresh)
- `revoked` (boolean): Whether the token has been revoked

## Password Reset Token Entity
**Description**: Represents a time-limited token for password recovery

**Fields**:
- `token` (string): The reset token string
- `user_id` (string): Reference to the user
- `expires_at` (datetime): When the token expires
- `used` (boolean): Whether the token has been used
- `created_at` (datetime): Token creation timestamp

## Relationships
- User (1) → (Many) Session: A user can have multiple active sessions
- User (1) → (Many) Authentication Token: A user can have multiple auth tokens
- User (1) → (Many) Password Reset Token: A user can have multiple reset tokens (though typically only one active)

## State Transitions

### User Account States
1. **Unverified**: After registration, email not verified
   - Can login but with limited access
   - Must verify email to get full access
2. **Active**: Email verified, account fully functional
   - Full access to all features
3. **Inactive**: Account deactivated by user or admin
   - Cannot login or access features
4. **Locked**: Temporarily locked due to security reasons
   - Cannot login for a specified period

### Session States
1. **Active**: Valid session that can be used for authentication
2. **Expired**: Session has passed its expiration time
3. **Revoked**: Session was explicitly invalidated by user or system

## Constraints
- User email must be unique across the system
- Password reset tokens must expire within 1 hour of creation
- Sessions should have reasonable expiration times (e.g., 7 days for "remember me", 1 hour for regular sessions)
- Only one active password reset token per user at a time
- User cannot have multiple accounts with the same email