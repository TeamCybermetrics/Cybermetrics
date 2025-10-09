# Cybermetrics Server

FastAPI backend for baseball player tracking with Firebase integration.

---

## 📐 Architecture & Structure

### Layer Flow
```
┌─────────────┐
│   Routes    │  API endpoints & request handling
└─────────────┘
       ↓
┌─────────────┐
│  Services   │  Business logic & data processing
└─────────────┘
       ↓
┌─────────────┐
│  Firebase   │  Authentication & Database
│  pybaseball │  Player data source
└─────────────┘
```

### Core Principle
**Separation of concerns through layers:**
- **Routes** handle HTTP requests/responses
- **Services** contain business logic
- **Models** validate data with Pydantic
- **Middleware** handles cross-cutting concerns (auth, errors)

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
├── services/           # Layer 2: Business Logic
│   ├── auth_service.py
│   ├── player_search_service.py
│   ├── saved_players_service.py
│   └── __init__.py
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
| Model | `feature.py` | snake_case |
| Middleware | `feature.py` | snake_case |

**Every directory must have `__init__.py`**

---

## 🔨 How to Add a New Route

### Structure
Routes define API endpoints. They handle HTTP and delegate logic to services.

### 1. Create Model (`models/stats.py`)
```python
from pydantic import BaseModel
from typing import Optional

class StatsRequest(BaseModel):
    player_id: int
    season: int

class StatsResponse(BaseModel):
    player_id: int
    batting_avg: float
    home_runs: int
    rbi: int
```

### 2. Create Service (`services/stats_service.py`)
```python
from fastapi import HTTPException, status
from models.stats import StatsResponse

class StatsService:
    """Service for handling player statistics"""
    
    async def get_stats(self, player_id: int, season: int) -> StatsResponse:
        """Get player stats for a specific season"""
        try:
            # Business logic here
            # Query database, process data, etc.
            
            return StatsResponse(
                player_id=player_id,
                batting_avg=0.300,
                home_runs=25,
                rbi=80
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch stats: {str(e)}"
            )

# Singleton instance
stats_service = StatsService()
```

### 3. Create Route (`routes/stats.py`)
```python
from fastapi import APIRouter, status, Depends
from models.stats import StatsRequest, StatsResponse
from services.stats_service import stats_service
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/stats", tags=["statistics"])

@router.get("/{player_id}", response_model=StatsResponse)
async def get_player_stats(
    player_id: int,
    season: int,
    current_user: str = Depends(get_current_user)  # Protected route
):
    """Get statistics for a specific player and season"""
    return await stats_service.get_stats(player_id, season)

@router.post("/", response_model=StatsResponse, status_code=status.HTTP_201_CREATED)
async def create_stats(stats_data: StatsRequest):
    """Create new player statistics (public route)"""
    return await stats_service.create_stats(stats_data)
```

### 4. Register Route (`routes/__init__.py`)
```python
from routes.auth import router as auth_router
from routes.players import router as players_router
from routes.stats import router as stats_router  # Add this

__all__ = ['auth_router', 'players_router', 'stats_router']
```

### 5. Include in Main App (`main.py`)
```python
from routes import auth_router, players_router, stats_router

app.include_router(auth_router)
app.include_router(players_router)
app.include_router(stats_router)  # Add this
```

---

## 🎬 How to Create Services

### Structure
Services contain business logic. They should NOT handle HTTP directly.

### Pattern (FOLLOW THIS EXACTLY)
```python
# services/feature_service.py
from fastapi import HTTPException, status
from models.feature import FeatureResponse
from config.firebase import firebase_service

class FeatureService:
    """Service for [feature description]"""
    
    def __init__(self):
        self.db = firebase_service.db
        # Initialize any resources
    
    async def method_name(self, param: str) -> FeatureResponse:
        """Method description"""
        # Validate Firebase/resources
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Business logic here
            result = self.db.collection('data').document(param).get()
            
            return FeatureResponse(data=result.to_dict())
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Operation failed: {str(e)}"
            )

# Singleton instance
feature_service = FeatureService()
```

### Service Rules
1. **Always use async methods** (`async def`)
2. **Always raise HTTPException** for errors
3. **Re-raise HTTPException** in except blocks (don't wrap twice)
4. **Return Pydantic models** for type safety
5. **Create singleton instance** at bottom of file

### Example: Complete Service
```python
# services/team_service.py
from fastapi import HTTPException, status
from models.teams import Team, TeamResponse
from config.firebase import firebase_service
from typing import List

class TeamService:
    """Service for managing baseball teams"""
    
    def __init__(self):
        self.db = firebase_service.db
    
    async def get_team(self, team_id: str) -> Team:
        """Get a specific team by ID"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            team_doc = self.db.collection('teams').document(team_id).get()
            
            if not team_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team {team_id} not found"
                )
            
            return Team(**team_doc.to_dict())
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get team: {str(e)}"
            )
    
    async def list_teams(self) -> List[Team]:
        """Get all teams"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            teams_ref = self.db.collection('teams').stream()
            return [Team(**doc.to_dict()) for doc in teams_ref]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list teams: {str(e)}"
            )

# Singleton
team_service = TeamService()
```

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
# ❌ WRONG - Logic in route
@router.get("/stats/{player_id}")
async def get_stats(player_id: int):
    db = firebase_service.db
    doc = db.collection('stats').document(str(player_id)).get()
    return doc.to_dict()

# ✅ CORRECT - Delegate to service
@router.get("/stats/{player_id}")
async def get_stats(player_id: int):
    return await stats_service.get_stats(player_id)
```

### 2. ❌ Never Forget Error Handling
```python
# ❌ WRONG - No error handling
async def get_data(self, id: str):
    return self.db.collection('data').document(id).get()

# ✅ CORRECT - Proper error handling
async def get_data(self, id: str):
    if not self.db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase is not configured"
        )
    
    try:
        doc = self.db.collection('data').document(id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data {id} not found"
            )
        return doc.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed: {str(e)}"
        )
```

### 3. ❌ Never Use Blocking I/O
```python
# ❌ WRONG - Blocking operation
def get_data():  # Not async!
    return requests.get('http://api.com/data')

# ✅ CORRECT - Async operation
async def get_data():
    async with httpx.AsyncClient() as client:
        return await client.get('http://api.com/data')
```

### 4. ❌ Never Skip Type Hints
```python
# ❌ WRONG - No types
def process_data(data):
    return data

# ✅ CORRECT - Full type hints
async def process_data(data: dict) -> ProcessedData:
    return ProcessedData(**data)
```

### 5. ❌ Never Return Raw Dictionaries
```python
# ❌ WRONG - Unvalidated dict
@router.get("/user/{id}")
async def get_user(id: str):
    return {"id": id, "name": "John"}

# ✅ CORRECT - Pydantic model
@router.get("/user/{id}", response_model=UserResponse)
async def get_user(id: str) -> UserResponse:
    return UserResponse(id=id, name="John")
```

### 6. ❌ Never Create Multiple Service Instances
```python
# ❌ WRONG - New instance each time
@router.get("/data")
async def get_data():
    service = DataService()  # NO!
    return await service.get()

# ✅ CORRECT - Use singleton
# In service file:
data_service = DataService()

# In route:
from services.data_service import data_service

@router.get("/data")
async def get_data():
    return await data_service.get()
```

### 7. ❌ Never Hardcode Values
```python
# ❌ WRONG - Hardcoded
FIREBASE_KEY = "path/to/key.json"

# ✅ CORRECT - Use config
from config.settings import settings
FIREBASE_KEY = settings.FIREBASE_CREDENTIALS_PATH
```

---

## 📋 Code Templates

### Route Template
```python
# routes/feature.py
from fastapi import APIRouter, status, Depends, Query
from models.feature import FeatureRequest, FeatureResponse
from services.feature_service import feature_service
from middleware.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/feature", tags=["feature"])

@router.get("/", response_model=List[FeatureResponse])
async def list_items():
    """Get all items (public)"""
    return await feature_service.list_all()

@router.get("/{item_id}", response_model=FeatureResponse)
async def get_item(item_id: str):
    """Get specific item by ID"""
    return await feature_service.get_by_id(item_id)

@router.post("/", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: FeatureRequest,
    current_user: str = Depends(get_current_user)
):
    """Create new item (protected)"""
    return await feature_service.create(current_user, data)

@router.put("/{item_id}", response_model=FeatureResponse)
async def update_item(
    item_id: str,
    data: FeatureRequest,
    current_user: str = Depends(get_current_user)
):
    """Update item (protected)"""
    return await feature_service.update(current_user, item_id, data)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete item (protected)"""
    await feature_service.delete(current_user, item_id)
```

### Service Template
```python
# services/feature_service.py
from fastapi import HTTPException, status
from config.firebase import firebase_service
from models.feature import FeatureRequest, FeatureResponse
from typing import List

class FeatureService:
    """Service for managing features"""
    
    def __init__(self):
        self.db = firebase_service.db
    
    async def list_all(self) -> List[FeatureResponse]:
        """Get all items"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            docs = self.db.collection('features').stream()
            return [FeatureResponse(**doc.to_dict()) for doc in docs]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list items: {str(e)}"
            )
    
    async def get_by_id(self, item_id: str) -> FeatureResponse:
        """Get specific item"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            doc = self.db.collection('features').document(item_id).get()
            
            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item {item_id} not found"
                )
            
            return FeatureResponse(**doc.to_dict())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get item: {str(e)}"
            )
    
    async def create(self, user_id: str, data: FeatureRequest) -> FeatureResponse:
        """Create new item"""
        if not self.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not configured"
            )
        
        try:
            # Create document
            doc_ref = self.db.collection('features').document()
            item_data = data.dict()
            item_data['id'] = doc_ref.id
            item_data['user_id'] = user_id
            
            doc_ref.set(item_data)
            
            return FeatureResponse(**item_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create item: {str(e)}"
            )

# Singleton
feature_service = FeatureService()
```

### Model Template
```python
# models/feature.py
from pydantic import BaseModel, Field
from typing import Optional

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
    user_id: str
    
    class Config:
        extra = "allow"
```

---

## ✅ Contribution Checklist

Before submitting a PR, verify:

### Structure
- [ ] Route files in `routes/` directory
- [ ] Service files in `services/` with `_service.py` suffix
- [ ] Model files in `models/` directory
- [ ] All directories have `__init__.py`
- [ ] Router registered in `routes/__init__.py`
- [ ] Router included in `main.py`

### Code Quality
- [ ] All functions are async (`async def`)
- [ ] Full type hints on all functions
- [ ] Services use singleton pattern
- [ ] Pydantic models for all request/response
- [ ] No business logic in routes
- [ ] Proper error handling (HTTPException)
- [ ] Re-raise HTTPException in services

### Security
- [ ] Protected routes use `Depends(get_current_user)`
- [ ] No hardcoded credentials
- [ ] Config values from `settings.py`

### Clean Up
- [ ] No print statements (use logger if needed)
- [ ] No commented code
- [ ] Code passes linting

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

**Remember the structure:**
1. **Routes** handle HTTP (endpoints only)
2. **Services** contain business logic
3. **Models** validate all data
4. **Use singletons** for services
5. **Always async** for I/O operations

**Follow the patterns, not your intuition.** This structure keeps the API maintainable, testable, and scalable.

