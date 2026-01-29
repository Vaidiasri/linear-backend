---
description: Comprehensive guide to planning and implementing a full-stack feature (Backend + Frontend)
---

# Feature Planning & Implementation Workflow

This workflow guides you through the process of planning, implementing, and verifying a new feature across the full stack.

## 1. Requirements & Scope Analysis

- [ ] **Define Objective**: What is the core goal of this feature?
- [ ] **Data Requirements**: What new data needs to be stored? (New tables, columns, relationships)
- [ ] **API Requirements**: What operations are needed? (CRUD: Create, Read, Update, Delete)
- [ ] **UI/UX Requirements**: How will the user interact with this? (New pages, modals, buttons, forms)

## 2. Backend Implementation (FastAPI/Python)

### Database Layer

- [ ] **Models**: Create or update SQLAlchemy models in `backend/app/models`.
- [ ] **Migrations** (if applicable): Generate and apply Alembic migrations.
  ```bash
  # Example (run in backend dir)
  alembic revision --autogenerate -m "add_feature_tables"
  alembic upgrade head
  ```

### Schema Layer

- [ ] **Pydantic Schemas**: Define Request (Create/Update) and Response schemas in `backend/app/schemas`.

### API Layer

- [ ] **Router**: Create a new router file in `backend/app/routers/` (e.g., `feature.py`).
- [ ] **Endpoints**: Implement the route handlers with proper status codes and error handling.
- [ ] **Registration**: Include the new router in `backend/app/main.py`.

## 3. Frontend Implementation (React/Vite)

### Data Layer

- [ ] **Types**: Add TypeScript interfaces for the new data structures.
- [ ] **API Client**: Add fetch/axios functions in `frontend/src/api` or `services`.
- [ ] **State Management**: Create React Query hooks (useQuery, useMutation) for data fetching/caching.

### UI Layer

- [ ] **Components**: Build small, reusable UI components (Buttons, Cards, Forms).
- [ ] **Page/Container**: Integrate components into a main page or container.
- [ ] **Routing**: Add the new route to `frontend/src/App.tsx` (or router config).

## 4. Verification & Testing

- [ ] **Backend Test**: Use Swagger UI (`http://localhost:8000/docs`) to manually test endpoints.
- [ ] **Frontend Test**: Check UI responsiveness, loading states, and error handling.
- [ ] **Integration**: Perform a full end-to-end user flow.
