# GitHub Actions CI Setup

## Overview

This project uses **two separate, independent CI pipelines**:

1. **Frontend CI** (`frontend-ci.yml`) - Tests React/Vite client
2. **Backend CI** (`backend-ci.yml`) - Tests FastAPI server

**Both pipelines must pass before a PR can be merged.**

### Smart Triggering
- **Frontend CI** only runs when files in `client/` change
- **Backend CI** only runs when files in `server/` change
- Both run in parallel and independently

---

## Quick Setup

### 1. Add Firebase Credentials Secret

**Required for Backend CI to work**

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `FIREBASE_CREDENTIALS`
5. Value: Paste the entire contents of `server/serviceAccountKey.json`
6. Click **Add secret**

### 2. Secure Your Credentials

Add to `.gitignore`:
```bash
server/serviceAccountKey.json
```

### 3. Push and Test

```bash
git add .
git commit -m "Add CI pipelines"
git push origin main
```

Check the **Actions** tab to see both pipelines run!

---

## How It Works

```
Pull Request Created
        ↓
   ┌────┴────┐
   ↓         ↓
Frontend CI  Backend CI
(separate)   (separate)
   ↓         ↓
 Install   Install
   ↓         ↓
  Build    Verify
   ↓         ↓
 Verify   Test Run
   ↓         ↓
   ✅        ✅
   └────┬────┘
        ↓
  Both Must Pass
        ↓
   PR Can Merge
```

---

## Viewing CI Results

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You'll see two workflows: **Frontend CI** and **Backend CI**
4. Click any run to see detailed logs
5. ✅ Green = Passed | ❌ Red = Failed

---

## What Gets Tested

### Frontend CI (`frontend-ci.yml`)
**Triggers:** Changes to `client/` folder
- ✅ Node.js 20 setup
- ✅ npm dependencies install (`npm ci`)
- ✅ TypeScript compilation
- ✅ Vite build succeeds (`npm run build`)
- ✅ Build artifacts created in `dist/`

### Backend CI (`backend-ci.yml`)
**Triggers:** Changes to `server/` folder
- ✅ Python 3.11 setup
- ✅ pip dependencies install
- ✅ Firebase credentials loaded from GitHub Secret
- ✅ All imports work (FastAPI, Firebase, Pybaseball, RapidFuzz)
- ✅ App can start (basic smoke test)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `FIREBASE_CREDENTIALS secret not found` | Add the secret in Settings → Secrets → Actions |
| `npm ci failed` | Ensure `client/package-lock.json` exists |
| `pip install failed` | Check `server/requirements.txt` is valid |
| `Import errors` | Verify all dependencies are in `requirements.txt` |
| Pipeline doesn't run | Check that files in `client/` or `server/` changed |

---

## Require CI Before Merging (Optional)

To prevent merging PRs with failing tests:

1. Go to **Settings** → **Branches**
2. Add branch protection rule for `main`
3. Enable **Require status checks to pass before merging**
4. Select **Frontend CI** and **Backend CI**
5. Save changes

Now PRs can only merge if both pipelines pass! ✅
