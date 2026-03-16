import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai # The new 2026 SDK
from models import SessionLocal, Product, engine, Base
from google.genai import types
from pydantic import BaseModel, ConfigDict
from typing import List
import logging # Added for professional tracking


load_dotenv()
# 1. Define what a Product looks like to the Frontend
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str
        

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
        
# Initialize the new Client
client = genai.Client(
    api_key=os.getenv("AI_API_KEY"),
    
)

app = FastAPI(title="Smart Semantic Search API",
    description="Vector-based search engine powered by Gemini and PGVector",
    version="1.0.0")

def get_embedding(text: str):
    """Generates a 3072-dimension vector using the correct model ID."""
    # 2. Use 'gemini-embedding-001' - NOT 'text-embedding-001'
    response = client.models.embed_content(
        model="gemini-embedding-001", 
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=3072 # Ensures it matches your DB schema
        )
    )
    return response.embeddings[0].values

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/search", response_model=List[ProductResponse])
def search(query: str, db: Session = Depends(get_db)):
    # 1. Handle Embedding Errors (External AI)
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="The AI search service is temporarily unavailable."
        )

    # 2. Handle Database Errors (Internal Infrastructure)
    try:
        results = db.query(Product).order_by(
            Product.embedding.l2_distance(query_vector)
        ).limit(5).all()
        
        return results
    except Exception as e:
        logger.error(f"Database Search Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while searching the database."
        )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Semantic Search API"}