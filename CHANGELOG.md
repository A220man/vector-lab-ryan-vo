# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-10-22

### Added
- FastAPI backend with REST API for documents, indexing, and chat
- React + TypeScript + Vite frontend with dashboard UI
- Hierarchical document indexing with tree structure
- Incremental index updates using node-level content hashing
- Document version history tracking
- Text-based index search with match type highlighting
- Chat interface with per-call LLM usage tracking
- Keycloak OIDC authentication integration (SAML broker ready)
- SQLite persistent storage with SQLAlchemy
- Docker Compose deployment with backend, frontend, Keycloak
- CI/CD pipeline with backend tests, frontend typecheck/build/test, Docker builds

### Fixed
- `get_leaf_nodes` KeyError bug (safe `.get()` access pattern)

### Security
- Non-root Docker users
- HttpOnly cookie-ready auth structure
- Environment-based secrets (no hardcoded credentials)