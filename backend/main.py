import os
import logging
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict

# Import only the Table model and Base to avoid immediate connection
from models import Product, Base

load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Schemas ---
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str

# --- Lazy Loading Factories ---

def get_ai_client():
    """Returns a GenAI client. Provides a dummy key if none is found for CI/CD safety."""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        logger.warning("AI_API_KEY not found. Falling back to dummy key for environment initialization.")
        return genai.Client(api_key="dummy_key")
    return genai.Client(api_key=api_key)

def get_db():
    """
    Creates a database session on demand. 
    By defining the engine here, we prevent connection errors during test imports.
    """
    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/postgres")
    
    # We create the engine inside the dependency so it doesn't run on module import
    engine = create_engine(database_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Core Logic ---

def get_embedding(text: str):
    """Generates a 3072-dimension vector using the GenAI client."""
    client = get_ai_client()
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=3072
            )
        )
        return response.embeddings[0].values
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="The AI search service is temporarily unavailable."
        )

# --- FastAPI App ---

app = FastAPI(
    title="Smart Semantic Search API",
    description="Vector-based search engine powered by Gemini and PGVector",
    version="1.0.0"
)

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Welcome to the Smart Semantic Search API"}

@app.get("/search", response_model=List[ProductResponse], tags=["Search"])
def search(query: str, db: Session = Depends(get_db)):
    # 1. Get Vector from AI
    query_vector = get_embedding(query)

    # 2. Perform Vector Search in Database
    try:
        results = db.query(Product).order_by(
            Product.embedding.l2_distance(query_vector)
        ).limit(5).all()
        
        return results
    except Exception as e:
        logger.error(f"Database Search Error: {str(e)}")
        # If this is called in CI/CD without a DB, this is where it would catch the error
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching the database."
        )