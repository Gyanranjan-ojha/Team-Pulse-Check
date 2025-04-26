# Team Pulse Check API Documentation

This document provides comprehensive information about the Team Pulse Check API endpoints, including request and response formats, authentication requirements, and example usage.

## Table of Contents

1. [Authentication](#authentication)
2. [Team APIs](#team-apis)
3. [User APIs](#user-apis)

## Authentication

All protected endpoints require authentication via a Bearer token in the Authorization header. The token is obtained from the login endpoint.

### Authentication Endpoints

#### Register User

```
POST /auth/register
```

Register a new user and send verification email.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "verification_email_sent": true,
  "verification_required": true
}
```

#### Send Verification Email

```
POST /auth/send-verification-email
```

Send or resend a verification email to a registered user.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Verification email sent successfully"
}
```

#### Verify Email (POST)

```
POST /auth/verify-email
```

Verify a user's email using the token sent to their email.

**Request Body:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Email verification successful"
}
```

#### Verify Email (GET)

```
GET /auth/verify-email/{token}
```

Alternative endpoint for email verification via direct link.

**Response (200 OK):**
```json
{
  "message": "Email verification successful"
}
```

#### Login

```
POST /auth/login
```

Authenticate a user and create a session.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "remember_me": true
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe"
  },
  "expires_at": "2023-08-01T12:00:00Z"
}
```

#### Logout

```
POST /auth/logout
```

Log out a user by invalidating their session.

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

#### Get Current User Info

```
GET /auth/me
```

Get information about the currently authenticated user.

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2023-07-01T10:00:00Z"
}
```

## Team APIs

### Team Management Endpoints

#### Create Team

```
POST /teams
```

Create a new team with the authenticated user as creator and admin.

**Request Body:**
```json
{
  "name": "My Team",
  "description": "A team for my project"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "My Team",
  "description": "A team for my project",
  "invite_code": "ABC123XYZ",
  "created_at": "2023-07-15T14:30:00Z",
  "updated_at": "2023-07-15T14:30:00Z"
}
```

#### Join Team

```
POST /teams/join
```

Join a team using an invite code.

**Request Body:**
```json
{
  "invite_code": "ABC123XYZ"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "My Team",
  "description": "A team for my project",
  "invite_code": "ABC123XYZ",
  "created_at": "2023-07-15T14:30:00Z",
  "updated_at": "2023-07-15T14:30:00Z"
}
```

#### Get My Teams

```
GET /teams/my
```

Get all teams that the current user is a member of.

**Response (200 OK):**
```json
[
  {
    "team": {
      "id": 1,
      "name": "My Team",
      "description": "A team for my project",
      "invite_code": "ABC123XYZ",
      "created_at": "2023-07-15T14:30:00Z",
      "updated_at": "2023-07-15T14:30:00Z"
    },
    "role": "admin",
    "joined_at": "2023-07-15T14:30:00Z"
  }
]
```

#### Get Team Information

```
GET /teams/{team_id}
```

Get information about a specific team. User must be a member of the team.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "My Team",
  "description": "A team for my project",
  "invite_code": "ABC123XYZ",
  "created_at": "2023-07-15T14:30:00Z",
  "updated_at": "2023-07-15T14:30:00Z"
}
```

#### Get Team Members

```
GET /teams/{team_id}/members
```

Get all members of a specific team. User must be a member of the team.

**Query Parameters:**
- `include_inactive` (boolean, optional): Whether to include inactive members

**Response (200 OK):**
```json
[
  {
    "user_id": 1,
    "username": "johndoe",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "admin",
    "joined_at": "2023-07-15T14:30:00Z",
    "is_active": true
  }
]
```

#### Update Team

```
PATCH /teams/{team_id}
```

Update team information. User must be an admin or creator of the team.

**Request Body:**
```json
{
  "name": "Updated Team Name",
  "description": "Updated team description"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Team Name",
  "description": "Updated team description",
  "invite_code": "ABC123XYZ",
  "created_at": "2023-07-15T14:30:00Z",
  "updated_at": "2023-07-15T15:45:00Z"
}
```

#### Regenerate Invite Code

```
POST /teams/{team_id}/regenerate-invite
```

Regenerate the invite code for a team. User must be an admin or creator.

**Response (200 OK):**
```json
{
  "invite_code": "XYZ789ABC"
}
```

#### Remove Team Member

```
DELETE /teams/{team_id}/members/{member_id}
```

Remove a member from a team. User must be an admin or creator of the team.

**Response (200 OK):**
```json
{
  "success": true
}
```

#### Invite User to Team

```
POST /teams/{team_id}/invitations
```

Invite a user to join a team. User must be a member of the team.

**Request Body:**
```json
{
  "invitee_email": "newuser@example.com"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "team_id": 1,
  "team_name": "My Team",
  "inviter_email": "user@example.com",
  "invitee_email": "newuser@example.com",
  "status": "pending",
  "expires_at": "2023-07-22T14:30:00Z",
  "created_at": "2023-07-15T14:30:00Z"
}
```

## Integration Guide for Frontend Developers

### Authentication Flow

1. Register a new user using `POST /auth/register`
2. User verifies their email by clicking the link in the verification email or using `POST /auth/verify-email`
3. User logs in using `POST /auth/login`
4. Store the returned token in localStorage or a secure cookie
5. Include the token in the Authorization header for all subsequent API calls:
   ```
   Authorization: Bearer your_token_here
   ```

### Team Management Flow

1. User creates a team using `POST /teams`
2. User can invite others to join the team using `POST /teams/{team_id}/invitations`
3. Other users can join the team using `POST /teams/join` with the invite code
4. Team information can be viewed using `GET /teams/{team_id}`
5. Team members can be viewed using `GET /teams/{team_id}/members`
6. Team admin can update team information using `PATCH /teams/{team_id}`
7. Team admin can remove members using `DELETE /teams/{team_id}/members/{member_id}`
8. Team admin can regenerate the invite code using `POST /teams/{team_id}/regenerate-invite`

### Error Handling

The API returns appropriate HTTP status codes for different error conditions:

- 400 Bad Request: Invalid request parameters or data
- 401 Unauthorized: Missing or invalid authentication token
- 403 Forbidden: Authenticated but not authorized to perform the action
- 404 Not Found: Resource not found
- 422 Unprocessable Entity: Invalid request body format
- 500 Internal Server Error: Server-side error

Error responses include a `detail` field with a descriptive error message: 