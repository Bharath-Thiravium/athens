# Project Code Explanation

## Frontend

The frontend is a React application structured with TypeScript and uses several modern libraries and patterns:

- **Entry Point**: `src/main.tsx`
  - Sets up React rendering with `createRoot`.
  - Wraps the app in `BrowserRouter` for routing.
  - Uses Ant Design's `ConfigProvider` with a custom theme.
  - Wraps the app in a custom `ThemeProvider` context for theming.
  - Suppresses specific Ant Design warnings in development.

- **Main App Component**: `src/app/App.tsx`
  - Handles routing using `react-router-dom`'s `Routes` and `Route`.
  - Uses `RoleBasedRoute` components to enforce role-based access control on routes.
  - Imports many feature components for different parts of the app:
    - Authentication (`signin`)
    - Dashboard
    - Projects
    - Admin management
    - User management
    - Company details
    - Chatbox
    - Manpower management
    - Worker management
    - Toolbox talks
    - Induction training
    - Job training
    - Minutes of Meeting (MOM)
    - Incident management
    - Safety observation
    - Permit to Work (PTW)
  - Uses React contexts for notifications and error boundaries.
  - Handles authentication state and redirects based on token and password reset status.

- **Code Organization**
  - Features are organized under `src/features/` with subfolders per feature.
  - Common utilities, hooks, contexts, and styles are under `src/common/`.
  - Assets like images are under `src/assets/`.
  - The app uses Ant Design UI components and custom theming.

## Backend

The backend is a Django 5.2.1 project with the following characteristics:

- **Project Structure**
  - Main Django project folder: `backend/`
    - Contains `settings.py`, `urls.py`, `asgi.py`, `wsgi.py`.
  - Multiple Django apps including:
    - `authentication`: Custom user model and authentication logic.
    - `chatbox`, `worker`, `tbt`, `inductiontraining`, `jobtraining`, `mom`, `safetyobservation`, `ptw`, `manpower`, etc.

- **Settings (`backend/settings.py`)**
  - Uses PostgreSQL as the database.
  - Configured with Django REST Framework and JWT authentication.
  - Uses Django Channels for WebSocket support with in-memory channel layer.
  - CORS configured to allow frontend origins.
  - Custom user model: `authentication.CustomUser`.
  - Logging configured with console and file handlers.
  - Security settings for production (SSL redirect, secure cookies).

- **Authentication App**
  - **Models (`authentication/models.py`)**
    - `Project`: Represents a project with categories and location details.
    - `CustomUser`: Extends Django's AbstractBaseUser with custom fields for user type, admin type, project association, and more.
    - `UserDetail`: Additional user details like employee ID, gender, documents, approval status.
    - `CompanyDetail`: Company information linked to a user.
    - Custom user manager handles user creation with default project assignment.

  - **Views (`authentication/views.py`)**
    - API views for user detail retrieval and update.
    - Company detail retrieval and update.
    - User approval endpoint.
    - JWT token obtain and logout views.
    - Project creation, listing, updating, and deletion.
    - Project admin user management: create, list, update, delete, password reset.
    - Master admin creation with uniqueness enforcement.
    - Various user listing endpoints filtered by roles.
    - Uses Django REST Framework generics and APIView classes.
    - Permissions enforced for master admin and authenticated users.

- **Other Backend Apps**
  - Other apps like `chatbox`, `worker`, `mom`, `ptw`, etc. are present but not detailed here.

## Summary

This project is a full-stack web application with a React frontend and Django backend. The frontend is organized with feature-based folders and uses role-based routing and theming. The backend uses Django REST Framework with JWT authentication, custom user models, and Channels for WebSocket support. The authentication app is a key part of the backend, managing users, projects, and permissions.

This explanation covers the main structure and key components of the frontend and backend codebases as currently read.
