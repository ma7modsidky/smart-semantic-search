import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai # The new 2026 SDK
from models import SessionLocal, Product, engine, Base
from google.genai import types
from pydantic import BaseModel
from typing import List

load_dotenv()
# 1. Define what a Product looks like to the Frontend
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True # This tells Pydantic to read data from SQLAlchemy models
        
        
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
    query_vector = get_embedding(query)
    
    # Semantic search
    results = db.query(Product).order_by(
        Product.embedding.l2_distance(query_vector)
    ).limit(5).all()
    
    return results