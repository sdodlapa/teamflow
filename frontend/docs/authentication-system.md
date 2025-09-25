# Frontend Authentication System Documentation

## Overview
The TeamFlow frontend now has a complete authentication system with React hooks, context providers, and routing protection. The system integrates with the FastAPI backend using JWT tokens.

## Architecture

### 1. Authentication Hook (`src/hooks/useAuth.ts`)
- **Purpose**: Core authentication logic with state management
- **Features**:
  - Login with email/password
  - Logout functionality
  - User registration/signup
  - Password reset requests
  - Profile updates
  - Automatic token management
- **State Management**: Uses React hooks (useState, useEffect, useCallback)
- **API Integration**: Communicates with FastAPI backend through apiClient

### 2. Authentication Context (`src/context/AuthContext.tsx`)
- **Purpose**: Provides authentication state throughout the app
- **Implementation**: React Context API wrapper around useAuth hook
- **Benefits**: Single source of truth for auth state across components

### 3. API Client (`src/services/apiClient.ts`)
- **Features**:
  - Axios-based HTTP client
  - Automatic token injection
  - Automatic token refresh on 401 errors
  - Consistent error handling
  - File upload support
- **Configuration**: Base URL from environment variables
- **Security**: JWT Bearer token authentication

### 4. Route Protection (`src/components/PrivateRoute.tsx`)
- **Purpose**: Protect routes that require authentication
- **Features**:
  - Automatic redirect to login for unauthenticated users
  - Loading state while checking authentication
  - Configurable redirect paths

### 5. Router Configuration (`src/router/AppRouter.tsx`)
- **Implementation**: React Router v6 with createBrowserRouter
- **Structure**:
  - Public routes: `/login`, `/register`
  - Protected routes: `/dashboard`, `/tasks`, `/projects`, etc.
  - Automatic redirects and fallbacks
- **Authentication**: Wrapped in AuthProvider for context access

### 6. Login Page (`src/pages/Login.tsx`)
- **Features**:
  - Email/password login form
  - Password reset functionality
  - Form validation and error handling
  - Responsive design with Tailwind CSS
  - Demo credentials display
  - Auto-redirect when already authenticated

## Key Features

### Authentication Flow
1. **Initial Load**: Check for existing tokens in localStorage
2. **Token Validation**: Verify token with backend `/auth/me` endpoint
3. **Auto-Refresh**: Automatically refresh expired tokens using refresh token
4. **Login**: Store JWT tokens on successful authentication
5. **Logout**: Clear tokens and redirect to login

### Security Features
- JWT access tokens (stored in localStorage)
- Refresh tokens for automatic session renewal
- Automatic token injection in API requests
- Secure logout with backend notification
- Route-level authentication protection

### User Experience
- Persistent login sessions
- Smooth loading states
- Toast notifications for user feedback
- Responsive design
- Clear error messaging

## API Integration

### Endpoints Used
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Token refresh
- `POST /auth/password-reset` - Password reset
- `GET /auth/me` - Get current user
- `PATCH /users/me` - Update profile

### Token Management
- **Access Token**: Short-lived (15 minutes), stored in localStorage
- **Refresh Token**: Long-lived (7 days), used for automatic renewal
- **Headers**: `Authorization: Bearer <access_token>`

## Environment Configuration

### Required Environment Variables
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Usage Examples

### Using Authentication in Components
```tsx
import { useAuthContext } from '../context/AuthContext';

const MyComponent = () => {
  const { user, isAuthenticated, logout } = useAuthContext();
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
};
```

### Protecting Routes
```tsx
<PrivateRoute>
  <DashboardPage />
</PrivateRoute>
```

### Making Authenticated API Calls
```tsx
import { apiClient } from '../services/apiClient';

const fetchUserData = async () => {
  try {
    const data = await apiClient.get('/users/me');
    return data;
  } catch (error) {
    console.error('Failed to fetch user data:', error);
  }
};
```

## Integration with Backend

### FastAPI Compatibility
- Compatible with TeamFlow's FastAPI authentication system
- Uses same JWT token format and refresh mechanism
- Matches backend API endpoint structure
- Handles backend error responses properly

### Multi-tenant Support
- User object includes `organizationId` for multi-tenant features
- Ready for role-based access control expansion

## Development Setup

### Running the Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testing Authentication
1. Start the backend server
2. Navigate to `http://localhost:3000`
3. Try accessing protected routes (should redirect to login)
4. Use demo credentials or register new account
5. Verify token persistence across browser refreshes

## Future Enhancements

### Planned Features
1. **Remember Me**: Optional long-term session persistence
2. **Social Login**: OAuth integration (Google, GitHub, etc.)
3. **Multi-factor Authentication**: SMS/Email verification
4. **Session Management**: View and revoke active sessions
5. **Role-based Access**: Component-level permission checks

### Security Improvements
1. **Token Security**: Consider using httpOnly cookies
2. **CSRF Protection**: Add CSRF token support
3. **Rate Limiting**: Implement client-side request throttling
4. **Session Timeout**: Warning before token expiration

## File Structure
```
src/
├── hooks/
│   └── useAuth.ts              # Core authentication hook
├── context/
│   └── AuthContext.tsx         # Authentication context provider
├── services/
│   └── apiClient.ts           # HTTP client with auth
├── components/
│   └── PrivateRoute.tsx       # Route protection component
├── router/
│   └── AppRouter.tsx          # Main routing configuration
├── pages/
│   └── Login.tsx              # Login page component
└── App.tsx                    # Main app with auth integration
```

This authentication system provides a solid foundation for the TeamFlow frontend, with proper security, user experience, and integration with the existing FastAPI backend.