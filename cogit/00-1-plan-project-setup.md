# 00-1: Project Setup and Initial Structure

## Objective
Set up the basic project structure with separate frontend and backend directories, initialize development environments, and create foundational configuration files.

## Prerequisites
- Git branch `refactor-volt` created
- `cog-it/` directory established

## Implementation Steps

### 1. Create Directory Structure
```bash
cog-it/
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── utils/
│   └── tests/
├── frontend/
│   ├── public/
│   ├── src/
│   └── tests/
├── docs/
└── scripts/
```

### 2. Backend Setup
- Create `backend/main.py` with basic FastAPI app
- Create `backend/requirements.txt` with core dependencies
- Set up `backend/.env.example` for environment variables
- Create `backend/pyproject.toml` for Python project configuration

### 3. Frontend Setup  
- Initialize Vite + React + TypeScript project in `frontend/`
- Configure Tailwind CSS
- Set up ESLint and Prettier
- Create basic folder structure in `src/`

### 4. Development Environment
- Create `docker-compose.dev.yml` for development
- Create `.gitignore` updates for new structure
- Set up `Makefile` for common development tasks

### 5. Documentation
- Create `README.md` with setup instructions
- Create `docs/API.md` for API documentation
- Create `docs/DEVELOPMENT.md` for development guide

## Files to Create
1. `backend/main.py`
2. `backend/requirements.txt`
3. `backend/.env.example`
4. `backend/pyproject.toml`
5. `frontend/package.json`
6. `frontend/vite.config.ts`
7. `frontend/tailwind.config.js`
8. `frontend/tsconfig.json`
9. `docker-compose.dev.yml`
10. `Makefile`
11. `README.md`

## Success Criteria
- [ ] Both backend and frontend can start without errors
- [ ] Hot reload works for both environments
- [ ] Basic API endpoint returns "Hello World"
- [ ] Frontend displays basic React page
- [ ] Docker containers start successfully

## Dependencies
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose

## Estimated Time
2-3 hours

## Next Steps
After completion, proceed to `00-2-plan-backend-core-structure.md`