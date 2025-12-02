# Cybermetrics

**2025 FTL BaiT Project**

A data-driven baseball roster analysis platform that helps teams identify weaknesses and find optimal player replacements

---

## Problem Domain & Problem Statement

Baseball roster management is complex. Teams need to understand:
- **Where is my team weak?** What skills are missing compared to league averages?
- **Which player should I replace?** Who's dragging the team down the most?
- **Who should I replace them with?** Which available players actually fix our specific problems?

Traditional approaches rely on gut instinct or generic player rankings (like WAR), but these don't account for team-specific needs. A high-WAR power hitter might make a strikeout-heavy team worse, not better.

**Cybermetrics solves this** by using statistical analysis to:
1. Calculate team weakness vectors using z-scores across 5 key offensive metrics
2. Identify the weakest player on your roster using adjustment scores
3. Simulate replacements and recommend players who specifically address your team's weaknesses

The result: **personalized, data-driven recommendations** instead of generic "best available" lists.

---

## Code Architecture

### Frontend Architecture (Client)

The client follows a **layered architecture** with strict separation of concerns:

```
Components → Pages → Actions → API → Backend
```

- **Components**: Reusable UI building blocks (Button, PlayerCard, Radar, etc.)
- **Pages**: Route-level components that assemble components
- **Actions**: Business logic and error handling layer
- **API**: HTTP communication layer (Axios wrapper)
- **Backend**: FastAPI server

**Naming Conventions:**
- Components/Pages: `PascalCase/` folders with `PascalCase.tsx` files
- Actions/API: `camelCase.ts` files
- Styles: `ComponentName.module.css` (CSS Modules)

### Backend Architecture (Server)

The server uses **Clean Architecture** with dependency injection:

```
Routes → Services → Domain → Infrastructure
```

- **Routes**: HTTP request/response handling (FastAPI endpoints)
- **Services**: Use case orchestration (no business logic)
- **Domain** (useCaseHelpers): Pure business logic and validation
- **Infrastructure**: External dependencies (Firebase, data access)
- **Repositories**: Abstract interfaces for data access

**Naming Conventions:**
- Files: `snake_case.py`
- Services: `feature_service.py`
- Domain: `feature_helper.py` (in `useCaseHelpers/`)
- Repositories: `feature_repository.py`

---

## Repository Organization

The repository is organized by **frontend/backend separation** with **layer-based structure** within each:

```
CybermetricsReal/
├── client/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level pages
│   │   ├── actions/        # Business logic layer
│   │   ├── api/            # HTTP client layer
│   │   └── config/         # Constants and configuration
│   └── package.json
│
└── server/                 # FastAPI + Python backend
    ├── routes/             # API endpoints
    ├── services/           # Use case orchestration
    ├── useCaseHelpers/     # Business logic (domain)
    ├── repositories/       # Abstract data interfaces
    ├── infrastructure/     # Concrete implementations (Firebase)
    ├── dtos/              # Data transfer objects
    ├── entities/          # Domain entities
    ├── middleware/        # Auth, error handling, rate limiting
    └── main.py            # FastAPI app entry point
```

**Key Principles:**
- **Frontend**: Layered architecture with one-way data flow
- **Backend**: Clean Architecture with dependency injection
- **Separation**: Frontend and backend are completely independent
- **Testing**: Both have comprehensive test suites

---

## System Architecture

### Tech Stack

**Frontend:**
- React 19 + TypeScript 5
- Vite 6 (build tool)
- React Router 7 (routing)
- Axios (HTTP client)
- CSS Modules (styling)

**Backend:**
- FastAPI (Python web framework)
- Python 3.10+
- Firebase Admin SDK (authentication & database)
- pybaseball (baseball data)
- Pydantic (data validation)
- Uvicorn (ASGI server)

### Hosting & Deployment

- **Frontend**: Hosted on Vercel at [https://cybermetrics.vercel.app/](https://cybermetrics.vercel.app/)
- **Backend**: FastAPI server (deploymed on Fly)
- **Database**: Firebase Firestore
- **Authentication**: Firebase Authentication (JWT tokens)

### System Connections

```
User Browser
    ↓
Vercel (Frontend)
    ↓ HTTPS
FastAPI Backend
    ↓
Firebase (Auth + Firestore)
    ↓
pybaseball (Baseball Data)
```

**Communication Flow:**
1. User interacts with React frontend on Vercel
2. Frontend makes API calls to FastAPI backend
3. Backend authenticates via Firebase Auth
4. Backend reads/writes data from Firestore
5. Backend fetches baseball statistics from pybaseball
6. Responses flow back through the stack

---

## User Guide

### For Baseball Managers & Analysts

**Persona**: You're a fantasy baseball manager or team analyst who needs to optimize your roster using data, not guesswork.

### Getting Started

1. **Sign Up**: Create an account at [https://cybermetrics.vercel.app/](https://cybermetrics.vercel.app/)
2. **Build Your Roster**: Navigate to "Team Builder" and add 9 players to your lineup
3. **View Team Analysis**: See your team's weakness vector visualized on a radar chart
4. **Get Recommendations**: Click "Get Recommendations" to see top 5 replacement candidates

### Key Features

**Team Builder**
- Add players by searching MLB player database
- View your roster with player cards showing key stats
- See team averages and league comparisons

**Team Analysis**
- Visualize team weaknesses using z-score radar chart
- Understand where your team underperforms league averages
- Identify which stats need improvement

**Player Recommendations**
- Automatically identifies weakest player on your roster
- Simulates replacements with all available players at that position
- Ranks candidates by how much they improve your team's weakness vector
- Shows improvement score for each recommendation

**Algorithm Explanation**
- Learn how z-scores work
- Understand adjustment scores and value scores
- See the mathematical foundation behind recommendations

### Understanding the Results

- **Weakness Vector**: Negative z-scores = weaknesses, positive = strengths
- **Adjustment Score**: How well a player addresses your team's weaknesses
- **Improvement Score**: How much a replacement reduces your total weakness
- **Recommendations**: Top 5 players ranked by improvement score

---

## Authors

Ethan Qui, Raymond Chan, Alec Jiang, Kahn Shah, Jayla Kwok

---

## Team Bios

**Techy Blinders** - 2025 FTL BaiT Project Team

We're a team of developers passionate about baseball analytics and data science. Cybermetrics combines our love of the game with modern web development and statistical analysis.

**Our Mission**: Make advanced baseball analytics accessible to everyone, from fantasy managers to professional analysts.

**Live Application**: [https://cybermetrics.vercel.app/](https://cybermetrics.vercel.app/)

---

## Features

- 🔐 **User Authentication**: Secure signup/login with Firebase Auth
- 📊 **Team Analysis**: Z-score based weakness vector visualization
- 🔍 **Player Search**: Search MLB player database with fuzzy matching
- 🎯 **Smart Recommendations**: Data-driven player replacement suggestions
- 📈 **Statistical Analysis**: Career averages, league comparisons, z-scores
- 🎨 **Modern UI**: Clean, responsive design with radar charts
- ⚡ **Fast Performance**: Optimized API calls and caching

---

## Development

### Code Quality

- **Frontend**: ESLint + TypeScript strict mode
- **Backend**: Pytest with comprehensive test coverage
- **Architecture**: Clean separation of concerns, dependency injection

---

## License

See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **pybaseball**: For providing comprehensive MLB statistics
- **Firebase**: For authentication and database infrastructure
- **FastAPI**: For the excellent Python web framework
- **React Team**: For the powerful UI library

---

