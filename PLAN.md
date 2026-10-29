# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

usage-measurement

## Roadmap

### project-skeleton — Project skeleton with FastAPI backend and React/Vite frontend

Status: done

Acceptance:
- Backend FastAPI app runs and serves /health endpoint
- Frontend React app builds and serves via Vite dev server
- Docker compose with backend, frontend, and Keycloak services
- Basic CI workflow runs backend and frontend tests

Implementation: `backend/app/main.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/src/main.tsx`, `docker-compose.yaml`, `.github/workflows/ci.yml`

Tests: `backend/tests/test_health.py`, `frontend/src/__tests__/DocumentList.test.tsx`, `frontend/src/__tests__/IndexView.test.tsx`, `frontend/src/__tests__/ChatView.test.tsx`

### incremental-indexing — Incremental index updates with content hashing

Status: done

Acceptance:
- Node-level content hashing detects changed sections between document versions
- Affected subtree rebuild only, not full tree
- Parent summaries recomputed along impacted paths
- Document version history maintained

Implementation: `backend/app/services/indexing.py`, `backend/app/api/routes/documents.py`

### usage-measurement — Per-call chat usage measurement across protocols

Status: done

Acceptance:
- Individual model-call records preserved with identity
- Complete/partial/unknown measurement states distinguished
- Cache-read, cache-write, reasoning quantities retained
- Measurements accessible on success, failure, cancellation

Implementation: `backend/app/models/__init__.py`, `backend/app/services/chat.py`, `backend/app/api/routes/chat.py`

### leaf-node-fix — Fix get_leaf_nodes KeyError on leaf nodes

Status: done

Acceptance:
- get_leaf_nodes safely handles nodes without 'nodes' key
- Returns leaf nodes correctly
- Consistent with .get() pattern used elsewhere

Implementation: `backend/app/services/indexing.py`

### pydantic-validation — Pydantic validation for LLM JSON outputs

Status: planned

Acceptance:
- Pydantic models validate LLM responses against schemas
- Malformed responses detected early with clear errors
- Applied to key output formats in indexing pipeline

### toc-page-offset-fix — Fix TypeError: unsupported operand for int + NoneType in TOC processing

Status: planned

Acceptance:
- add_page_offset_to_toc_json handles None page values
- Graceful handling of missing page numbers
- No crash on incomplete TOC data

