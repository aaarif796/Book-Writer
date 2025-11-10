# Book Writer AI — Robust Scaffold

This enhanced scaffold includes:
- Async FastAPI backend with improved error handling and logging.
- Crew-style YAML agent configs and a CrewManager that supports OpenAI/HuggingFace (if configured).
- FAISS handler and embedding utility (with a deterministic demo embedder fallback).
- React frontend served in Docker Compose.
- Dockerfile + docker-compose (backend + mysql + frontend)
- Basic GitHub Actions workflow for lint & tests.

Add API keys to `.env` and run with Docker Compose or locally.