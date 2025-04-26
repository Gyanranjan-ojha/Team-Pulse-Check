# Team-Pulse-Check

## Overview

Team-Pulse-Check is a passive team activity and collaboration tracker designed to provide visibility into team health signals. It surfaces early warnings for burnout, overload, and disengagement through an intuitive dashboard that visualizes commits, pull requests, messages, blockers, and other team activities. This tool helps team leaders and members monitor team health and take proactive measures to maintain productivity and well-being.

## Features

- **Authentication & Team Management:** Secure email-based signup/login with team creation and joining capabilities.
- **Activity Tracking:** Monitoring of commits, PRs, Slack messages, and blocker flags.
- **Team Pulse Dashboard:** Visual representation of team activity over time.
- **Early Warning System:** Identification of potential burnout, overload, or disengagement.
- **Activity Simulation Engine:** Generation of mock activity data for testing and demonstration.
- **Secure Data Handling:** Team-scoped data access to ensure privacy and security.
- **Metrics & Aggregation:** Analysis of team and individual activity patterns.
- **Real-time Analytics:** Up-to-date insights into team collaboration dynamics.

## Project Structure

```bash
Team-Pulse-Check/
├── .env                    # Environment variables configuration
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
├── frontend/               # Frontend application code
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context providers
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service functions
│   │   ├── types/          # TypeScript type definitions
│   │   ├── utils/          # Utility functions
│   │   └── App.tsx         # Main application component
│   ├── package.json        # NPM dependencies
│   └── tsconfig.json       # TypeScript configuration
├── backend/                # Backend application code
│   ├── requirements.txt    # Python dependencies
│   ├── src/
│   │   ├── db/             # Database models and connection
│   │   ├── routers/        # API route definitions
│   │   ├── schemas/        # Pydantic schemas for validation
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions and helpers
│   │   └── main.py         # Application entry point
├── .venv/                  # Python virtual environment
└── logs/                   # Application logs
```

## Prerequisites

Before installing Team-Pulse-Check, ensure you have the following installed:

- Python (version 3.10 or higher)
- Node.js and npm (latest stable versions)
- Database system (PostgreSQL or MongoDB)

## Installation

### 1. Clone the project

```bash
git clone https://github.com/your-username/Team-Pulse-Check.git
```

### 2. Navigate to the project directory

```bash
cd Team-Pulse-Check
```

## Backend Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\activate
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Create a `.env` file in the root directory with the following variables:

```bash
# Environment
ENVIRONMENT="development"

# Database Configuration
DATABASE_URL=

# JWT Configuration
JWT_SECRET=
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# API Configuration
HOST=localhost
PORT=8000

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

# Logging Configuration
LOG_LEVEL=INFO
```

### 5. Set up the database

```bash
python -m backend.src.db.create_tables
```

## Running the Application

### Start the backend server

```bash
cd backend
python -m src.main
```

The API will be available at: http://localhost:8000/api/

### Start the frontend development server

Navigate to the frontend directory and run:

```bash
cd frontend
npm install
npm start
```

The frontend will be available at: http://localhost:8080

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs

## Database Schema

The database consists of the following main models:

1. **User:** Stores user information (id, email, password hash, team ID, creator status)
2. **Team:** Contains team data (id, name, invite code, creator ID)
3. **Activity:** Records team activities (id, user ID, team ID, type, timestamp)
