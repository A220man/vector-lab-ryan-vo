# Changelog

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added
- `add_page_offset_to_toc_json` function for TOC page offset handling with None value support
- Recursive processing of nested TOC children
- Comprehensive test suite (11 tests) for TOC page offset functionality
## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added
- Pydantic validation models for LLM JSON outputs (NodeSummaryOutput, NodeStructureOutput, DocumentAnalysisOutput, ChatResponseOutput)
- Validation utilities: `validate_llm_json_output()` and `safe_parse_llm_json()` with fallback support
- Integration with indexing pipeline for summary generation (`generate_node_summary`, `generate_node_summary_safe`, `update_node_summary`)
- Test endpoint `/api/v1/index/validate-summary` for validation testing
- Comprehensive test suite (18 tests) for validation models and utilities

### Fixed
- `get_leaf_nodes` KeyError bug (safe `.get()` access pattern)
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