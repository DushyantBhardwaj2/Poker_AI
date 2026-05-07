# 🔐 PokerSense AI - Authentication Setup Guide

This project uses **Neon Auth** for secure, production-ready identity management. Follow these steps to configure the authentication system.

## 🛠️ Environment Variables

Add the following to your `apps/web/.env` or `apps/web/.env.local`:

```bash
# --- NEON AUTH CONFIGURATION ---
# Found in Neon Console -> Project -> Auth -> Configuration
PUBLIC_NEON_AUTH_URL=https://auth.neon.com/your-project-id

# --- GOOGLE OAUTH CONFIGURATION ---
# Obtained from Google Cloud Console
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# --- REDIRECTS ---
# Where the user is sent after login (usually the root)
AUTH_REDIRECT_URL=http://localhost:4321/
```

## 🚀 Google OAuth Setup Instructions

1.  **Google Cloud Console**:
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    -   Create a new project or select an existing one.
    -   Navigate to **APIs & Services > Credentials**.
    -   Click **Create Credentials > OAuth client ID**.
    -   Choose **Web application**.
    -   Add **Authorized redirect URIs**:
        -   `https://auth.neon.com/_auth/callback` (Standard Neon Auth callback)
        -   `http://localhost:4321/_auth/callback` (For local development if using a local auth proxy)
    -   Copy the **Client ID** and **Client Secret**.

2.  **Neon Console**:
    -   Navigate to your project in the [Neon Console](https://console.neon.tech/).
    -   Go to **Auth > Configuration**.
    -   Enable **Google** as a social provider.
    -   Enter the **Client ID** and **Client Secret** obtained from Google.
    -   Save the changes.

## 🧩 Authentication Flow

- **Login**: Users can sign in via Google OAuth or Email/Password.
- **Session Persistence**: Authentication state is managed by `@neondatabase/auth`. Tokens are stored in cookies/localStorage and automatically refreshed.
- **Protection**: Routes are protected via the `AuthGuard` component. Public access is granted to any route starting with `/auth/`.
- **Logout**: Handled via `authClient.signOut()` which clears the session and redirects to the login portal.

## 🎨 Aesthetic Integration

The authentication UI has been custom-built to match the **PokerSense Tactical HUD** aesthetic:
- **Dark Theme**: Charcoal and Gold color palette.
- **Tactical Elements**: Scanning line animations, glowing corners, and monospace typography.
- **Minimalist**: Removed all "Elite" and "Premium" marketing language to focus on system utility.
