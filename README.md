# 🔍 Smart Semantic Search (AI-Powered)

A professional full-stack search engine that leverages **Vector Embeddings** to understand user intent beyond simple keyword matching. Unlike traditional keyword search, this system finds products based on semantic meaning using high-dimensional AI models.

---

## 🏗️ Architecture Overview

This project is built as a containerized monorepo, optimized for developer experience and production-ready performance.

* **Frontend**: Next.js 14+ (App Router) utilizing **Framer Motion** for staggered entrance animations and **Tailwind CSS** for styling.
* **Backend**: FastAPI (Python 3.11) managing semantic logic and REST endpoints.
* **Vector DB**: **PostgreSQL 17** with the **pgvector** extension for high-performance 3072-dimension similarity searches.
* **AI Layer**: Google Gemini AI for generating high-fidelity embeddings.

## 🛠️ Engineering Features

* **Multi-Stage Docker Builds**: Optimized images that separate build-time dependencies from the final production runner to minimize image size.
* **Automated CI/CD**: A GitHub Actions pipeline with **path-filtering** to independently test the frontend (Vitest) and backend (Pytest).
* **Persistent DX**: Utilizes **Named Docker Volumes** for `node_modules` and build caches to ensure lightning-fast container startups and consistent environments across different host OSs.
* **Semantic Similarity**: Implements vector-based discovery rather than basic string matching.

## 🚦 Getting Started

### 1. Prerequisites
* Docker and Docker Compose installed.
* A Google Gemini API Key.

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
AI_API_KEY=your_gemini_api_key_here
```
### 3. Launch the Stack
```bash
# Builds and starts all services (DB, Backend, Frontend)
docker compose up --build
# Seed the DB with products
docker compose exec backend python seed.py
```
* Frontend: http://localhost:3000
* API Docs: http://localhost:8000/docs

## 🧪4. Testing
Both layers are fully tested via containerized runners to ensure environment parity between local development and CI.

```bash
# Run Frontend Integration Tests (Vitest + JSDOM)
docker compose exec frontend npx vitest run

# Run Backend Unit Tests (Pytest)
docker compose exec backend pytest
```

---
## 📁 Project Structure
```
.
├── .github/workflows/  # Automated CI/CD pipelines
├── backend/            # FastAPI, AI logic, and Pytest suite
├── frontend/           # Next.js app, Vitest suite, and Tailwind config
├── docker-compose.yml  # Multi-container orchestration
└── .env                # Local environment variables (Git ignored)
```