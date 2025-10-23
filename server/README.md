# Cybermetrics Server

FastAPI backend for baseball player tracking with Firebase integration, built using Clean Architecture principles.

---

## 📐 Architecture & Structure

### Clean Architecture Layers
```
┌─────────────────┐
│     Routes      │  API endpoints & HTTP handling
└─────────────────┘
         ↓
┌─────────────────┐
│    Services     │  Use Cases - Pure orchestration
└─────────────────┘
         ↓
┌─────────────────┐
│     Domain      │  Business logic & validation rules
└─────────────────┘
         ↓
┌─────────────────┐
│ Infrastructure  │  Firebase, external APIs, data access
└─────────────────┘
```

### Core Principles
**Clean Architecture with Dependency Injection:**
- **Routes** handle HTTP requests/responses only
- **Services** orchestrate between domain and infrastructure (no business logic)
- **Domain** contains pure business logic and validation rules
- **Infrastructure** handles external dependencies (Firebase, APIs)
- **Dependency Injection** wires everything together cleanly

---

## 📁 File Structure

```
server/
├── routes/              # Layer 1: API Endpoints
│   ├── auth.py         # /api/auth/*
│   ├── players.py      # /api/players/*
│   ├── health.py       # /api/health
│   └── __init__.py     # Router exports
│
├── services/           # Layer 2: Use Cases (Orchestration)
│   ├── auth_service.py
│   ├── player_search_service.py
│   ├── saved_players_service.py
│   ├── roster_avg_service.py
│   └── __init__.py
│
├── domain/             # Layer 3: Business Logic
│   ├── auth_domain.py
│   ├── player_domain.py
│   ├── saved_players_domain.py
│   └── roster_domain.py
│
├── repositories/       # Layer 4: Abstract Interfaces (Ports)
│   ├── auth_repository.py
│   ├── player_repository.py
│   ├── saved_players_repository.py
│   └── roster_repository.py
│
├── infrastructure/     # Layer 5: Concrete Implementations (Adapters)
│   ├── auth_repository.py
│   ├── player_repository.py
│   ├── saved_players_repository.py
│   └── roster_repository.py
│
├── dependency/         # Dependency Injection Container
│   └── dependencies.py # Factory functions for all services
│
├── models/             # Data Models (Pydantic)
│   ├── auth.py
│   ├── players.py
│   └── __init__.py
│
├── middleware/         # Cross-cutting Concerns
│   ├── auth.py         # JWT verification
│   ├── error_handler.py
│   └── __init__.py
│
├── config/             # Configuration
│   ├── settings.py     # Environment variables
│   ├── firebase.py     # Firebase initialization
│   └── __init__.py
│
├── utils/              # Utilities
│   ├── logger.py
│   └── __init__.py
│
├── main.py            # FastAPI app entry point
└── requirements.txt   # Dependencies
```

### File Naming Rules

| Type | File | Pattern |
|------|------|---------|
| Route | `feature.py` | snake_case |
| Service | `feature_service.py` | snake_case + `_service` suffix |
| Domain | `feature_domain.py` | snake_case + `_domain` suffix |
| Repository (Abstract) | `feature_repository.py` | snake_case + `_repository` suffix |
| Infrastructure | `feature_repository.py` | snake_case + `_repository` suffix |
| Model | `feature.py` | snake_case |
| Middleware | `feature.py` | snake_case |

**Every directory must have `__init__.py`**

---

## 🎯 Understanding Clean Architecture

### What Each Layer Does

**Routes (API Layer)**
- Handle HTTP requests and responses
- Validate input using Pydantic models
- Call services and return responses
- NO business logic here!

**Services (Use Cases)**
- Orchestrate between domain and infrastructure
- Coordinate multiple operations
- Handle the "what" of business operations
- NO direct database access or business rules

**Domain (Business Logic)**
- Contains pure business logic and rules
- Validates business constraints
- Calculates complex business operations
- NO external dependencies (Firebase, APIs, etc.)

**Repositories (Abstract Interfaces)**
- Define contracts for data access
- Abstract away implementation details
- Allow easy testing and swapping implementations

**Infrastructure (Concrete Implementations)**
- Implements repository interfaces
- Handles Firebase, external APIs, file I/O
- Contains all external dependencies
- Can be swapped out without changing business logic

### Dependency Injection

Instead of creating objects inside classes, we inject them from the outside:

```python
# ❌ OLD WAY - Hard to test, tightly coupled
class AuthService:
    def __init__(self):
        self.db = firebase_service.db  # Hard dependency

# ✅ NEW WAY - Easy to test, loosely coupled
class AuthService:
    def __init__(self, auth_repository: AuthRepository, auth_domain: AuthDomain):
        self.auth_repository = auth_repository  # Injected dependency
        self.auth_domain = auth_domain
```

**Benefits:**
- Easy to test (inject mock objects)
- Easy to swap implementations
- Clear separation of concerns
- Follows dependency inversion principle

## 🔨 How to Add a New Feature (Complete Example)

Let's say you want to add a "teams" feature. Here's the complete process:

### 1. Create Models (`models/teams.py`)
```python
from pydantic import BaseModel
from typing import Optional, List

class TeamRequest(BaseModel):
    name: str
    city: str
    league: str

class TeamResponse(BaseModel):
    id: str
    name: str
    city: str
    league: str
    created_at: str
```

### 2. Create Domain (`domain/teams_domain.py`)
```python
from fastapi import HTTPException, status

class TeamsDomain:
    """Pure business logic for teams"""
    
    def __init__(self):
        pass
    
    def validate_team_name(self, name: str) -> None:
        """Validate team name business rules"""
        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team name must be at least 2 characters"
            )
    
    def validate_league(self, league: str) -> None:
        """Validate league business rules"""
        valid_leagues = ["AL", "NL", "MLB"]
        if league not in valid_leagues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"League must be one of: {valid_leagues}"
            )
```

### 3. Create Repository Interface (`repositories/teams_repository.py`)
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from models.teams import TeamResponse

class TeamsRepository(ABC):
    """Abstract interface for teams data access"""
    
    @abstractmethod
    async def create_team(self, team_data: dict) -> TeamResponse:
        pass
    
    @abstractmethod
    async def get_team(self, team_id: str) -> Optional[TeamResponse]:
        pass
    
    @abstractmethod
    async def get_all_teams(self) -> List[TeamResponse]:
        pass
```

### 4. Create Infrastructure (`infrastructure/teams_repository.py`)
```python
from repositories.teams_repository import TeamsRepository
from models.teams import TeamResponse
from fastapi import HTTPException, status
from typing import List, Optional

class TeamsRepositoryFirebase(TeamsRepository):
    """Firebase implementation of teams repository"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_team(self, team_data: dict) -> TeamResponse:
        """Create team in Firebase"""
        try:
            doc_ref = self.db.collection('teams').document()
            team_data['id'] = doc_ref.id
            doc_ref.set(team_data)
            return TeamResponse(**team_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create team: {str(e)}"
            )
    
    async def get_team(self, team_id: str) -> Optional[TeamResponse]:
        """Get team from Firebase"""
        try:
            doc = self.db.collection('teams').document(team_id).get()
            if not doc.exists:
                return None
            return TeamResponse(**doc.to_dict())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get team: {str(e)}"
            )
    
    async def get_all_teams(self) -> List[TeamResponse]:
        """Get all teams from Firebase"""
        try:
            docs = self.db.collection('teams').stream()
            return [TeamResponse(**doc.to_dict()) for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get teams: {str(e)}"
            )
```

### 5. Create Service (`services/teams_service.py`)
```python
from repositories.teams_repository import TeamsRepository
from domain.teams_domain import TeamsDomain
from models.teams import TeamRequest, TeamResponse
from typing import List

class TeamsService:
    """Service for managing teams - pure orchestration"""
    
    def __init__(self, teams_repository: TeamsRepository, teams_domain: TeamsDomain):
        self.teams_repository = teams_repository
        self.teams_domain = teams_domain
    
    async def create_team(self, team_request: TeamRequest) -> TeamResponse:
        """Create a new team"""
        # Validate business rules
        self.teams_domain.validate_team_name(team_request.name)
        self.teams_domain.validate_league(team_request.league)
        
        # Convert to dict and create
        team_data = team_request.dict()
        return await self.teams_repository.create_team(team_data)
    
    async def get_team(self, team_id: str) -> TeamResponse:
        """Get team by ID"""
        team = await self.teams_repository.get_team(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team {team_id} not found"
            )
        return team
    
    async def get_all_teams(self) -> List[TeamResponse]:
        """Get all teams"""
        return await self.teams_repository.get_all_teams()
```

### 6. Add to Dependencies (`dependency/dependencies.py`)
```python
# Add these imports at the top
from infrastructure.teams_repository import TeamsRepositoryFirebase
from domain.teams_domain import TeamsDomain
from services.teams_service import TeamsService

# Add these factory functions
def get_teams_repository() -> TeamsRepository:
    return TeamsRepositoryFirebase(firebase_service.db)

def get_teams_domain() -> TeamsDomain:
    return TeamsDomain()

def get_teams_service() -> TeamsService:
    return TeamsService(get_teams_repository(), get_teams_domain())
```

### 7. Create Route (`routes/teams.py`)
```python
from fastapi import APIRouter, status, Depends
from models.teams import TeamRequest, TeamResponse
from services.teams_service import TeamsService
from dependency.dependencies import get_teams_service
from typing import List

router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_request: TeamRequest,
    teams_service: TeamsService = Depends(get_teams_service)
):
    """Create a new team"""
    return await teams_service.create_team(team_request)

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    teams_service: TeamsService = Depends(get_teams_service)
):
    """Get team by ID"""
    return await teams_service.get_team(team_id)

@router.get("/", response_model=List[TeamResponse])
async def get_all_teams(
    teams_service: TeamsService = Depends(get_teams_service)
):
    """Get all teams"""
    return await teams_service.get_all_teams()
```

### 8. Register Route (`routes/__init__.py`)
```python
from routes.auth import router as auth_router
from routes.players import router as players_router
from routes.teams import router as teams_router  # Add this

__all__ = ['auth_router', 'players_router', 'teams_router']
```

### 9. Include in Main App (`main.py`)
```python
from routes import auth_router, players_router, teams_router

app.include_router(auth_router)
app.include_router(players_router)
app.include_router(teams_router)  # Add this
```

---

---

## 🎬 How Each Layer Works

### Routes Layer
Routes are thin - they just handle HTTP and delegate to services:

```python
# routes/teams.py
@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_request: TeamRequest,
    teams_service: TeamsService = Depends(get_teams_service)  # Dependency injection
):
    """Create a new team"""
    return await teams_service.create_team(team_request)  # Delegate to service
```

**Rules:**
- Only handle HTTP concerns (status codes, response models)
- Use dependency injection for services
- Delegate all logic to services
- No business logic here!

### Services Layer
Services orchestrate between domain and infrastructure:

```python
# services/teams_service.py
class TeamsService:
    def __init__(self, teams_repository: TeamsRepository, teams_domain: TeamsDomain):
        self.teams_repository = teams_repository  # Injected
        self.teams_domain = teams_domain          # Injected
    
    async def create_team(self, team_request: TeamRequest) -> TeamResponse:
        # 1. Validate business rules (domain)
        self.teams_domain.validate_team_name(team_request.name)
        
        # 2. Convert and save (infrastructure)
        team_data = team_request.dict()
        return await self.teams_repository.create_team(team_data)
```

**Rules:**
- Pure orchestration - no business logic
- No direct database access
- Coordinate between domain and infrastructure
- Always async methods

### Domain Layer
Domain contains pure business logic:

```python
# domain/teams_domain.py
class TeamsDomain:
    def validate_team_name(self, name: str) -> None:
        """Pure business rule validation"""
        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team name must be at least 2 characters"
            )
```

**Rules:**
- Pure business logic only
- No external dependencies (no Firebase, no APIs)
- Can raise HTTPException for validation errors
- Easy to test in isolation

### Infrastructure Layer
Infrastructure handles external dependencies:

```python
# infrastructure/teams_repository.py
class TeamsRepositoryFirebase(TeamsRepository):
    def __init__(self, db):
        self.db = db  # Firebase injected
    
    async def create_team(self, team_data: dict) -> TeamResponse:
        """Firebase-specific implementation"""
        doc_ref = self.db.collection('teams').document()
        team_data['id'] = doc_ref.id
        doc_ref.set(team_data)
        return TeamResponse(**team_data)
```

**Rules:**
- Implements repository interfaces
- Handles all external dependencies
- Can be swapped out easily
- Contains Firebase, API calls, file I/O

---

## 📦 How to Create Models

### Structure
Models use Pydantic for validation. Create request/response pairs.

### Pattern (FOLLOW THIS EXACTLY)
```python
# models/feature.py
from pydantic import BaseModel, Field
from typing import Optional

# Request model (input validation)
class FeatureRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: int = Field(..., ge=0, le=100)
    optional_field: Optional[str] = None

# Response model (output structure)
class FeatureResponse(BaseModel):
    id: str
    name: str
    value: int
    created_at: str
    
    class Config:
        # Allow extra fields from Firestore
        extra = "allow"
```

### Validation Examples
```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserRequest(BaseModel):
    email: EmailStr  # Auto email validation
    age: int = Field(..., ge=18, le=120)  # Min/max
    username: str = Field(..., min_length=3, max_length=20)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v
```

### Common Patterns
```python
# Optional field with default
status: str = "pending"

# Optional field (can be None)
description: Optional[str] = None

# Union types (Python 3.10+)
count: int | None = None

# List validation
tags: List[str] = []

# Nested models
class Address(BaseModel):
    street: str
    city: str

class User(BaseModel):
    name: str
    address: Address
```

---

## 🔐 Authentication & Dependencies

### Protected Routes (Require Auth)
```python
from fastapi import Depends
from middleware.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    """This route requires authentication"""
    # current_user is the user_id (uid) from JWT token
    return {"user_id": current_user}
```

### Public Routes (No Auth)
```python
@router.get("/public")
async def public_route():
    """This route is publicly accessible"""
    return {"message": "Hello, world!"}
```

### How Auth Works
1. Client sends `Authorization: Bearer {token}` header
2. `get_current_user` dependency extracts and validates token
3. Returns `user_id` if valid, raises 401 if invalid
4. Route receives `user_id` as parameter

---

## 🚫 Things NOT to Do

### 1. ❌ Never Put Business Logic in Routes
```python
# ❌ WRONG - Business logic in route
@router.post("/teams")
async def create_team(team_data: TeamRequest):
    if len(team_data.name) < 2:  # Business rule in route!
        raise HTTPException(status_code=400, detail="Name too short")
    return await teams_service.create_team(team_data)

# ✅ CORRECT - Delegate to service
@router.post("/teams")
async def create_team(team_data: TeamRequest, teams_service: TeamsService = Depends(get_teams_service)):
    return await teams_service.create_team(team_data)  # Service handles validation
```

### 2. ❌ Never Put Business Logic in Services
```python
# ❌ WRONG - Business logic in service
class TeamsService:
    async def create_team(self, team_data: TeamRequest):
        if len(team_data.name) < 2:  # Business rule in service!
            raise HTTPException(status_code=400, detail="Name too short")
        return await self.repository.create_team(team_data)

# ✅ CORRECT - Business logic in domain
class TeamsService:
    async def create_team(self, team_data: TeamRequest):
        self.teams_domain.validate_team_name(team_data.name)  # Domain handles validation
        return await self.repository.create_team(team_data)
```

### 3. ❌ Never Access External Dependencies in Domain
```python
# ❌ WRONG - Firebase in domain
class TeamsDomain:
    def validate_team(self, team_data: dict):
        db = firebase_service.db  # External dependency in domain!
        existing = db.collection('teams').where('name', '==', team_data['name']).get()
        if existing:
            raise HTTPException(status_code=400, detail="Team exists")

# ✅ CORRECT - Pure business logic in domain
class TeamsDomain:
    def validate_team_name(self, name: str):
        if not name or len(name.strip()) < 2:  # Pure business rule
            raise HTTPException(status_code=400, detail="Name too short")
```

### 4. ❌ Never Skip Dependency Injection
```python
# ❌ WRONG - Hard dependencies
class TeamsService:
    def __init__(self):
        self.db = firebase_service.db  # Hard dependency, hard to test

# ✅ CORRECT - Dependency injection
class TeamsService:
    def __init__(self, teams_repository: TeamsRepository, teams_domain: TeamsDomain):
        self.teams_repository = teams_repository  # Injected, easy to test
        self.teams_domain = teams_domain
```

### 5. ❌ Never Create Objects Inside Classes
```python
# ❌ WRONG - Creating dependencies inside
class TeamsService:
    async def create_team(self, team_data: TeamRequest):
        domain = TeamsDomain()  # Creating dependency inside!
        domain.validate_team_name(team_data.name)

# ✅ CORRECT - Inject dependencies
class TeamsService:
    def __init__(self, teams_domain: TeamsDomain):
        self.teams_domain = teams_domain  # Injected from outside
    
    async def create_team(self, team_data: TeamRequest):
        self.teams_domain.validate_team_name(team_data.name)
```

### 6. ❌ Never Skip Repository Interfaces
```python
# ❌ WRONG - Direct Firebase access in service
class TeamsService:
    def __init__(self, db):
        self.db = db  # Direct Firebase dependency
    
    async def create_team(self, team_data: dict):
        doc_ref = self.db.collection('teams').document()  # Firebase code in service!

# ✅ CORRECT - Use repository interface
class TeamsService:
    def __init__(self, teams_repository: TeamsRepository):
        self.teams_repository = teams_repository  # Abstract interface
    
    async def create_team(self, team_data: dict):
        return await self.teams_repository.create_team(team_data)  # Clean abstraction
```

### 7. ❌ Never Mix Concerns
```python
# ❌ WRONG - Mixed concerns
class TeamsService:
    async def create_team(self, team_data: TeamRequest):
        # Validation (domain concern)
        if len(team_data.name) < 2:
            raise HTTPException(status_code=400, detail="Name too short")
        
        # Database access (infrastructure concern)
        doc_ref = self.db.collection('teams').document()
        doc_ref.set(team_data.dict())
        
        # Business logic (domain concern)
        if team_data.league == "MLB":
            team_data.premium = True

# ✅ CORRECT - Separated concerns
class TeamsService:
    async def create_team(self, team_data: TeamRequest):
        self.teams_domain.validate_team_name(team_data.name)  # Domain
        return await self.teams_repository.create_team(team_data)  # Infrastructure
```

---

## 📋 Code Templates

### Complete Feature Template

Here's a complete template for adding any new feature following Clean Architecture:

#### 1. Model (`models/feature.py`)
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class FeatureRequest(BaseModel):
    """Request model for creating/updating feature"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    value: int = Field(..., ge=0)

class FeatureResponse(BaseModel):
    """Response model for feature"""
    id: str
    name: str
    description: Optional[str] = None
    value: int
    created_at: str
    
    class Config:
        extra = "allow"
```

#### 2. Domain (`domain/feature_domain.py`)
```python
from fastapi import HTTPException, status

class FeatureDomain:
    """Pure business logic for features"""
    
    def __init__(self):
        pass
    
    def validate_feature_name(self, name: str) -> None:
        """Validate feature name business rules"""
        if not name or len(name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feature name must be at least 2 characters"
            )
    
    def validate_feature_value(self, value: int) -> None:
        """Validate feature value business rules"""
        if value < 0 or value > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feature value must be between 0 and 1000"
            )
```

#### 3. Repository Interface (`repositories/feature_repository.py`)
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from models.feature import FeatureResponse

class FeatureRepository(ABC):
    """Abstract interface for feature data access"""
    
    @abstractmethod
    async def create_feature(self, feature_data: dict) -> FeatureResponse:
        pass
    
    @abstractmethod
    async def get_feature(self, feature_id: str) -> Optional[FeatureResponse]:
        pass
    
    @abstractmethod
    async def get_all_features(self) -> List[FeatureResponse]:
        pass
    
    @abstractmethod
    async def update_feature(self, feature_id: str, feature_data: dict) -> FeatureResponse:
        pass
    
    @abstractmethod
    async def delete_feature(self, feature_id: str) -> bool:
        pass
```

#### 4. Infrastructure (`infrastructure/feature_repository.py`)
```python
from repositories.feature_repository import FeatureRepository
from models.feature import FeatureResponse
from fastapi import HTTPException, status
from typing import List, Optional

class FeatureRepositoryFirebase(FeatureRepository):
    """Firebase implementation of feature repository"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_feature(self, feature_data: dict) -> FeatureResponse:
        """Create feature in Firebase"""
        try:
            doc_ref = self.db.collection('features').document()
            feature_data['id'] = doc_ref.id
            doc_ref.set(feature_data)
            return FeatureResponse(**feature_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create feature: {str(e)}"
            )
    
    async def get_feature(self, feature_id: str) -> Optional[FeatureResponse]:
        """Get feature from Firebase"""
        try:
            doc = self.db.collection('features').document(feature_id).get()
            if not doc.exists:
                return None
            return FeatureResponse(**doc.to_dict())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get feature: {str(e)}"
            )
    
    async def get_all_features(self) -> List[FeatureResponse]:
        """Get all features from Firebase"""
        try:
            docs = self.db.collection('features').stream()
            return [FeatureResponse(**doc.to_dict()) for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get features: {str(e)}"
            )
    
    async def update_feature(self, feature_id: str, feature_data: dict) -> FeatureResponse:
        """Update feature in Firebase"""
        try:
            doc_ref = self.db.collection('features').document(feature_id)
            doc_ref.update(feature_data)
            updated_doc = doc_ref.get()
            return FeatureResponse(**updated_doc.to_dict())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update feature: {str(e)}"
            )
    
    async def delete_feature(self, feature_id: str) -> bool:
        """Delete feature from Firebase"""
        try:
            self.db.collection('features').document(feature_id).delete()
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete feature: {str(e)}"
            )
```

#### 5. Service (`services/feature_service.py`)
```python
from repositories.feature_repository import FeatureRepository
from domain.feature_domain import FeatureDomain
from models.feature import FeatureRequest, FeatureResponse
from fastapi import HTTPException, status
from typing import List

class FeatureService:
    """Service for managing features - pure orchestration"""
    
    def __init__(self, feature_repository: FeatureRepository, feature_domain: FeatureDomain):
        self.feature_repository = feature_repository
        self.feature_domain = feature_domain
    
    async def create_feature(self, feature_request: FeatureRequest) -> FeatureResponse:
        """Create a new feature"""
        # Validate business rules
        self.feature_domain.validate_feature_name(feature_request.name)
        self.feature_domain.validate_feature_value(feature_request.value)
        
        # Convert to dict and create
        feature_data = feature_request.dict()
        return await self.feature_repository.create_feature(feature_data)
    
    async def get_feature(self, feature_id: str) -> FeatureResponse:
        """Get feature by ID"""
        feature = await self.feature_repository.get_feature(feature_id)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature {feature_id} not found"
            )
        return feature
    
    async def get_all_features(self) -> List[FeatureResponse]:
        """Get all features"""
        return await self.feature_repository.get_all_features()
    
    async def update_feature(self, feature_id: str, feature_request: FeatureRequest) -> FeatureResponse:
        """Update feature"""
        # Validate business rules
        self.feature_domain.validate_feature_name(feature_request.name)
        self.feature_domain.validate_feature_value(feature_request.value)
        
        # Check if feature exists
        existing = await self.feature_repository.get_feature(feature_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature {feature_id} not found"
            )
        
        # Update
        feature_data = feature_request.dict()
        return await self.feature_repository.update_feature(feature_id, feature_data)
    
    async def delete_feature(self, feature_id: str) -> bool:
        """Delete feature"""
        # Check if feature exists
        existing = await self.feature_repository.get_feature(feature_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature {feature_id} not found"
            )
        
        return await self.feature_repository.delete_feature(feature_id)
```

#### 6. Dependencies (`dependency/dependencies.py`)
```python
# Add these imports at the top
from infrastructure.feature_repository import FeatureRepositoryFirebase
from domain.feature_domain import FeatureDomain
from services.feature_service import FeatureService

# Add these factory functions
def get_feature_repository() -> FeatureRepository:
    return FeatureRepositoryFirebase(firebase_service.db)

def get_feature_domain() -> FeatureDomain:
    return FeatureDomain()

def get_feature_service() -> FeatureService:
    return FeatureService(get_feature_repository(), get_feature_domain())
```

#### 7. Route (`routes/feature.py`)
```python
from fastapi import APIRouter, status, Depends
from models.feature import FeatureRequest, FeatureResponse
from services.feature_service import FeatureService
from dependency.dependencies import get_feature_service
from middleware.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/features", tags=["features"])

@router.post("/", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_request: FeatureRequest,
    current_user: str = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service)
):
    """Create a new feature (protected)"""
    return await feature_service.create_feature(feature_request)

@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: str,
    feature_service: FeatureService = Depends(get_feature_service)
):
    """Get feature by ID (public)"""
    return await feature_service.get_feature(feature_id)

@router.get("/", response_model=List[FeatureResponse])
async def get_all_features(
    feature_service: FeatureService = Depends(get_feature_service)
):
    """Get all features (public)"""
    return await feature_service.get_all_features()

@router.put("/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: str,
    feature_request: FeatureRequest,
    current_user: str = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service)
):
    """Update feature (protected)"""
    return await feature_service.update_feature(feature_id, feature_request)

@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: str,
    current_user: str = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service)
):
    """Delete feature (protected)"""
    await feature_service.delete_feature(feature_id)
```

---

## ✅ Contribution Checklist

Before submitting a PR, verify:

### Clean Architecture Structure
- [ ] Route files in `routes/` directory (HTTP only)
- [ ] Service files in `services/` with `_service.py` suffix (orchestration only)
- [ ] Domain files in `domain/` with `_domain.py` suffix (business logic only)
- [ ] Repository interfaces in `repositories/` directory (abstract contracts)
- [ ] Infrastructure implementations in `infrastructure/` directory (concrete implementations)
- [ ] Model files in `models/` directory (Pydantic validation)
- [ ] All directories have `__init__.py`
- [ ] Router registered in `routes/__init__.py`
- [ ] Router included in `main.py`
- [ ] Dependencies added to `dependency/dependencies.py`

### Code Quality
- [ ] All functions are async (`async def`)
- [ ] Full type hints on all functions
- [ ] Services use dependency injection (no singletons)
- [ ] Pydantic models for all request/response
- [ ] No business logic in routes
- [ ] No business logic in services (only orchestration)
- [ ] No external dependencies in domain
- [ ] Proper error handling (HTTPException)
- [ ] Repository interfaces implemented correctly

### Dependency Injection
- [ ] Services receive dependencies through constructor
- [ ] Dependencies injected via FastAPI `Depends()`
- [ ] Factory functions in `dependency/dependencies.py`
- [ ] No hard dependencies or global state

### Security
- [ ] Protected routes use `Depends(get_current_user)`
- [ ] No hardcoded credentials
- [ ] Config values from `settings.py`

### Clean Up
- [ ] No print statements (use logger if needed)
- [ ] No commented code
- [ ] Code passes linting
- [ ] No unused imports

### Commits
- [ ] Commit message follows convention:
  - `feat:` New feature
  - `fix:` Bug fix
  - `refactor:` Code restructuring
  - `docs:` Documentation

---

## 🔧 Common Tasks

### Add query parameters
```python
@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),  # Required
    limit: int = Query(10, ge=1, le=100),  # Optional with default
    offset: int = 0
):
    return await service.search(q, limit, offset)
```

### Add request headers
```python
@router.get("/data")
async def get_data(
    x_custom_header: str = Header(None)
):
    return {"header": x_custom_header}
```

### File upload
```python
from fastapi import File, UploadFile

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename}
```

### Custom dependency
```python
async def verify_api_key(api_key: str = Header(...)):
    if api_key != "secret":
        raise HTTPException(status_code=403)
    return api_key

@router.get("/protected")
async def protected(api_key: str = Depends(verify_api_key)):
    return {"status": "authorized"}
```

---

## 🛠 Tech Stack

- **FastAPI** - Web framework
- **Python 3.10** - Language
- **Pydantic** - Data validation
- **Firebase Admin SDK** - Auth & database
- **pybaseball** - Baseball data
- **rapidfuzz** - Fuzzy matching
- **Uvicorn** - ASGI server

---

## 📝 Summary

**Clean Architecture Principles:**
1. **Routes** handle HTTP only (no business logic)
2. **Services** orchestrate between domain and infrastructure (no business logic)
3. **Domain** contains pure business logic (no external dependencies)
4. **Infrastructure** handles external dependencies (Firebase, APIs)
5. **Dependency Injection** wires everything together cleanly
6. **Repository Pattern** abstracts data access
7. **Always async** for I/O operations

**Key Benefits:**
- **Testable** - Easy to mock dependencies
- **Maintainable** - Clear separation of concerns
- **Flexible** - Easy to swap implementations
- **Scalable** - Clean boundaries between layers

**Follow the patterns, not your intuition.** This Clean Architecture structure keeps the API maintainable, testable, and scalable for years to come.

