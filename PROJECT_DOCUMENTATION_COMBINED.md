# UpatePro - Comprehensive EHS Management System Documentation

---

## Frontend Setup and Overview

### Frontend Framework and Tools

- React 19.1.0 with TypeScript
- Vite 6.3.5 as build tool
- UI Libraries: Ant Design 5.25.1, Mantine, Heroicons, Tabler Icons, Lucide React, React Icons
- State Management: Zustand
- Routing: React Router DOM 7.6.0
- Styling: Tailwind CSS 4.1.10, styled-components 6.1.18
- HTTP Client: Axios 1.9.0
- Additional Libraries: Framer Motion, Moment.js, React Hook Form, Leaflet, Recharts

### Environment Setup

1. Copy environment file:
```bash
cp .env.example .env
```

2. Update `.env` with backend API URL:
```
VITE_API_BASE_URL=http://localhost:8000
```

3. Install dependencies and start development server:
```bash
pnpm install
pnpm dev
```

---

## Backend Setup and Overview

### Backend Framework and Tools

- Django 5.2.1 with Django REST Framework 3.16.0
- PostgreSQL database
- JWT Authentication with SimpleJWT 5.5.0
- Django Channels 4.2.2 for WebSocket support
- Redis for channel layers
- Additional libraries: django-cors-headers, face-recognition, OpenCV, psycopg2-binary

### Backend Setup Instructions

1. Install required packages:
```bash
pip install channels channels-redis
```

2. Update Django settings (`settings.py`) to include channels and Redis configuration.

3. Create ASGI application (`asgi.py`) with ProtocolTypeRouter and WebSocket routing.

4. Add models, consumers, routing, admin configuration, and utility functions for notifications.

5. Run migrations:
```bash
python manage.py makemigrations authentication
python manage.py migrate
```

6. Install and start Redis server.

---

## Project Overview and Architecture

(Include the full content of PROJECT_COMPLETE_DOCUMENTATION.md here, covering:)

- Project overview and technology stack
- System architecture (frontend and backend folder structures)
- Core system features (authentication, safety observation, worker management, PTW, incident management, MOM, training, manpower, chat)
- Advanced features (real-time notifications, digital signature, theme system, security)
- Database schema overview
- API endpoints overview
- Frontend components architecture and state management
- File upload and management
- Workflow management
- Reporting and analytics
- Integration capabilities and mobile compatibility
- Deployment and configuration
- Performance optimizations
- Security considerations
- Maintenance and monitoring
- Future enhancements
- Development guidelines

---

This document provides a comprehensive overview of the UpatePro EHS management system, including setup, architecture, features, and development guidelines.
