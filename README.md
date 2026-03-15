# Smart Semantic Search 🔍

A full-stack search engine that understands **intent**, not just keywords. 
Built with a FastAPI/Python backend, PostgreSQL + PGVector, and Next.js.

## 🚀 Features
- **Semantic Understanding:** Uses Google Gemini AI to generate 3072-dimension embeddings.
- **Vector Storage:** High-performance similarity search using PGVector on PostgreSQL 17.
- **Containerized:** Fully Dockerized environment for one-command deployment.
- **FastAPI:** Modern, high-performance API with automated Swagger documentation.

## 🛠️ Tech Stack
- **Backend:** FastAPI, SQLAlchemy, Google GenAI SDK.
- **Database:** PostgreSQL + PGVector.
- **Infrastructure:** Docker, Docker Compose.

## 🚦 Quick Start
1. Clone the repo.
2. Create a `.env` file in the root and add `AI_API_KEY=your_gemini_key`.
3. Run `docker compose up --build`.
4. Access the API docs at `http://localhost:8000/docs`.