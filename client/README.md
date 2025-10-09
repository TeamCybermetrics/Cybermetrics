# Cybermetrics Client

React + TypeScript frontend for baseball player tracking.

---

## 📐 Architecture & Structure

### Layer Flow
```
┌─────────────┐
│ Components  │  Reusable UI building blocks
└─────────────┘
       ↓
┌─────────────┐
│   Pages     │  Components assembled into routes
└─────────────┘
       ↓
┌─────────────┐
│  Actions    │  Business logic & error handling
└─────────────┘
       ↓
┌─────────────┐
│     API     │  HTTP communication with backend
└─────────────┘
       ↓
┌─────────────┐
│   Backend   │  FastAPI server
└─────────────┘
```

### Core Principle
**Each layer only talks to the layer directly below it.**
- Components build Pages
- Pages call Actions
- Actions call API
- API calls Backend

---

## 📁 File Structure

```
src/
├── components/          # Layer 1: UI Components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.module.css
│   │   └── index.ts
│   ├── Input/
│   ├── PlayerCard/
│   └── ...
│
├── pages/              # Layer 2: Route Pages
│   ├── LandingPage/
│   │   ├── LandingPage.tsx
│   │   ├── LandingPage.module.css
│   │   └── index.ts
│   ├── LoginPage/
│   ├── DashboardPage/
│   └── ...
│
├── actions/            # Layer 3: Business Logic
│   ├── auth.ts
│   ├── players.ts
│   └── ...
│
├── api/                # Layer 4: HTTP Layer
│   ├── client.ts      # Axios instance (DO NOT MODIFY)
│   ├── auth.ts
│   ├── players.ts
│   └── ...
│
├── config/
│   ├── constants.ts   # API URLs, storage keys
│   └── index.ts
│
├── App.tsx            # Route definitions
└── main.tsx           # Entry point
```

### File Naming Rules

| Type | Folder | File | Style |
|------|--------|------|-------|
| Component | `PascalCase/` | `PascalCase.tsx` | `PascalCase.module.css` |
| Page | `PascalCase/` | `PascalCase.tsx` | `PascalCase.module.css` |
| Action | N/A | `camelCase.ts` | N/A |
| API | N/A | `camelCase.ts` | N/A |

**Every component/page folder must have:**
- Main file: `ComponentName.tsx`
- Styles: `ComponentName.module.css`
- Barrel export: `index.ts`

---

## 🔨 How to Add a New Page

### Structure
```
src/pages/NewPage/
├── NewPage.tsx
├── NewPage.module.css
└── index.ts
```

### 1. Create Component (`NewPage.tsx`)
```typescript
import { useState, useEffect } from 'react';
import styles from './NewPage.module.css';
import { Button } from '@/components';
import { myActions } from '@/actions/myActions';

export default function NewPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const result = await myActions.getData();
      
      if (result.success) {
        setData(result.data);
      } else {
        setError(result.error);
      }
      setLoading(false);
    };
    
    loadData();
  }, []);

  return (
    <div className={styles.container}>
      <h1>New Page</h1>
      {/* Your UI */}
    </div>
  );
}
```

### 2. Create Barrel Export (`index.ts`)
```typescript
export { default } from './NewPage';
```

### 3. Add Route (`App.tsx`)
```typescript
import NewPage from '@/pages/NewPage';

<Route path="/new" element={<NewPage />} />
```

---

## 🎬 How to Create Actions

### Structure
Actions live in `src/actions/` as single files (no folders).

### Pattern (FOLLOW THIS EXACTLY)
```typescript
// src/actions/myActions.ts
import { myApi } from '@/api/myApi';

export const myActions = {
  // Action name should be descriptive
  actionName: async (param: Type) => {
    try {
      // Call the API layer
      const result = await myApi.endpoint(param);
      
      // Return success format
      return { success: true, data: result };
    } catch (error) {
      // Return error format
      return {
        success: false,
        error: error instanceof Error ? error.message : "Operation failed",
      };
    }
  },
};
```

### Required Format
**All actions MUST return:**
```typescript
{ success: true, data: T } | { success: false, error: string }
```

### Example
```typescript
// src/actions/stats.ts
import { statsApi } from '@/api/stats';

export const statsActions = {
  getPlayerStats: async (playerId: number) => {
    try {
      const stats = await statsApi.getStats(playerId);
      return { success: true, data: stats };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to fetch stats",
      };
    }
  },

  updateStats: async (playerId: number, stats: PlayerStats) => {
    try {
      const updated = await statsApi.updateStats(playerId, stats);
      return { success: true, data: updated };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to update stats",
      };
    }
  },
};
```

### How to Call Actions (in Pages/Components)
```typescript
// Always handle both success and error cases
const result = await myActions.actionName(param);

if (result.success) {
  // Use result.data
  setData(result.data);
} else {
  // Handle result.error
  setError(result.error);
}
```

---

## 🌐 How to Create API Calls

### Structure
API files live in `src/api/` as single files (no folders).

### Pattern (FOLLOW THIS EXACTLY)
```typescript
// src/api/myApi.ts
import { apiClient } from './client';

// Define response types
interface MyResponse {
  id: number;
  name: string;
}

export const myApi = {
  // Method name describes the action
  getItem: async (id: number): Promise<MyResponse> => {
    return apiClient.get<MyResponse>(`/api/items/${id}`);
  },

  createItem: async (data: Partial<MyResponse>): Promise<MyResponse> => {
    return apiClient.post<MyResponse>('/api/items', data);
  },

  updateItem: async (id: number, data: Partial<MyResponse>): Promise<MyResponse> => {
    return apiClient.put<MyResponse>(`/api/items/${id}`, data);
  },

  deleteItem: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/api/items/${id}`);
  },
};
```

### Available HTTP Methods
```typescript
apiClient.get<T>(url)              // GET
apiClient.post<T>(url, body)       // POST
apiClient.put<T>(url, body)        // PUT
apiClient.delete<T>(url)           // DELETE
apiClient.patch<T>(url, body)      // PATCH
```

### Authentication
**Auth headers are automatic.** Do NOT manually add auth headers.

```typescript
// ✅ CORRECT - Auth token auto-injected by apiClient
const players = await playersApi.getSaved();

// ❌ WRONG - Never do this
axios.get('/api/players', {
  headers: { Authorization: `Bearer ${token}` }
});
```

---

## 🚫 Things NOT to Do

### 1. ❌ Never Skip Layers
```typescript
// ❌ WRONG - Page calling API directly
export default function MyPage() {
  const data = await myApi.getData();  // NO!
}

// ✅ CORRECT - Page → Action → API
export default function MyPage() {
  const result = await myActions.getData();
}
```

### 2. ❌ Never Use `any` Type
```typescript
// ❌ WRONG
function Component(props: any) { }
const data: any = await api.call();

// ✅ CORRECT
interface Props { name: string; }
function Component(props: Props) { }
const data: MyType = await api.call();
```

### 3. ❌ Never Make Components Without Barrel Exports
```
// ❌ WRONG Structure
Button/
├── Button.tsx
└── Button.module.css

// ✅ CORRECT Structure
Button/
├── Button.tsx
├── Button.module.css
└── index.ts  ← REQUIRED
```

### 4. ❌ Never Use Inline Styles
```typescript
// ❌ WRONG
<div style={{ color: 'red', padding: '10px' }}>

// ✅ CORRECT - Use CSS Modules
<div className={styles.container}>
```

### 5. ❌ Never Manually Handle Auth
```typescript
// ❌ WRONG
const token = localStorage.getItem('auth_token');
axios.get(url, { headers: { Authorization: `Bearer ${token}` } });

// ✅ CORRECT
apiClient.get(url);  // Auth auto-added
```

### 6. ❌ Never Forget Error Handling
```typescript
// ❌ WRONG
const data = await myActions.getData();
setData(data.data);  // What if it failed?

// ✅ CORRECT
const result = await myActions.getData();
if (result.success) {
  setData(result.data);
} else {
  setError(result.error);
}
```

### 7. ❌ Never Leave Debug Code
```typescript
// ❌ WRONG - Remove before commit
console.log('debug:', data);
debugger;

// ✅ CORRECT - Clean code
```

---

## 📋 Code Templates

### Component Template
```typescript
// src/components/ComponentName/ComponentName.tsx
import { useState } from 'react';
import styles from './ComponentName.module.css';

interface ComponentNameProps {
  title: string;
  onAction?: () => void;
}

export default function ComponentName({ title, onAction }: ComponentNameProps) {
  const [state, setState] = useState('');

  const handleEvent = () => {
    // Logic here
    onAction?.();
  };

  return (
    <div className={styles.container}>
      <h2>{title}</h2>
    </div>
  );
}
```

```typescript
// src/components/ComponentName/index.ts
export { default } from './ComponentName';
```

### Page Template
```typescript
// src/pages/PageName/PageName.tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './PageName.module.css';
import { Button } from '@/components';
import { myActions } from '@/actions/myActions';

export default function PageName() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    const result = await myActions.getData();
    
    if (result.success) {
      setData(result.data);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className={styles.container}>
      <h1>Page Name</h1>
      {loading && <p>Loading...</p>}
      {error && <p className={styles.error}>{error}</p>}
      {data && <div>{/* Display data */}</div>}
    </div>
  );
}
```

```typescript
// src/pages/PageName/index.ts
export { default } from './PageName';
```

### Action Template
```typescript
// src/actions/featureName.ts
import { featureApi } from '@/api/featureName';

export const featureActions = {
  doSomething: async (param: string) => {
    try {
      const result = await featureApi.endpoint(param);
      return { success: true, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Operation failed",
      };
    }
  },
};
```

### API Template
```typescript
// src/api/featureName.ts
import { apiClient } from './client';

interface FeatureResponse {
  id: number;
  name: string;
}

export const featureApi = {
  endpoint: async (param: string): Promise<FeatureResponse> => {
    return apiClient.get<FeatureResponse>(`/api/feature/${param}`);
  },
};
```

---

## ✅ Contribution Checklist

Before submitting a PR, verify:

### Structure
- [ ] Files follow naming conventions (PascalCase/camelCase)
- [ ] Components/Pages have folder with tsx + css + index.ts
- [ ] Actions/API are single files in their directories
- [ ] Barrel exports (index.ts) created for all components/pages

### Code Quality
- [ ] All actions return `{ success, data?, error? }`
- [ ] No direct API calls in components/pages
- [ ] TypeScript types defined (no `any`)
- [ ] Error handling implemented
- [ ] CSS Modules used for styling (no inline styles)

### Clean Up
- [ ] No `console.log` or debug statements
- [ ] No commented-out code
- [ ] `npm run build` passes
- [ ] `npm run lint` passes

### Commits
- [ ] Commit message follows convention:
  - `feat:` New feature
  - `fix:` Bug fix
  - `refactor:` Code restructuring
  - `style:` Formatting only

---

## 🔧 Common Tasks

### Add a new route
```typescript
// App.tsx
import MyPage from '@/pages/MyPage';
<Route path="/my-page" element={<MyPage />} />
```

### Navigate programmatically
```typescript
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/dashboard');
```

### Use localStorage (with constants)
```typescript
import { STORAGE_KEYS } from '@/config';

// Store
localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);

// Retrieve
const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

// Remove
localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
```

### Check authentication
```typescript
import { authActions } from '@/actions/auth';
const isAuth = authActions.isAuthenticated();
```

---

## 🛠 Tech Stack

- **React 19** - UI framework
- **TypeScript 5** - Type safety
- **Vite 6** - Build tool & dev server
- **React Router 7** - Routing
- **Axios** - HTTP client (wrapped in apiClient)
- **CSS Modules** - Component-scoped styling

---

## 📝 Summary

**Remember the structure:**
1. **Components** are building blocks
2. **Pages** assemble components
3. **Pages** call **Actions**
4. **Actions** call **API**
5. **API** talks to backend

**Follow the patterns, not your intuition.** This structure keeps the codebase maintainable and predictable.
