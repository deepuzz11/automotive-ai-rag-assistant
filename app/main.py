from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import os
import logging
from .core.embeddings import engine
from .core.rag import rag_assistant
from .core.recommender import recommender
from .models import (
    SearchRequest, SearchResult, 
    AskRequest, AskResponse, 
    RecommendRequest, RecommendResponse, Recommendation
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load data and build index
    logger.info("Starting up Automotive AI Assistant...")
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    engine.load_data(data_dir)
    yield
    # Shutdown: Clean up if needed
    logger.info("Shutting down Automotive AI Assistant...")

app = FastAPI(
    title="Ford Vehicle Intelligence System",
    description="Mini AI-Powered Automotive Knowledge Assistant for Ford Vehicles",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Ford Vehicle Intelligence System API"}

@app.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    """Semantic Search for Vehicle Knowledge."""
    try:
        results = engine.search(request.query)
        return [
            SearchResult(
                content=res['content'],
                source=res['metadata']['source'],
                id=res['metadata']['id'],
                score=res['score']
            ) for res in results
        ]
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal search engine error")

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """RAG-Based Automotive Assistant."""
    try:
        # 1. Retrieve relevant context
        context_docs = engine.search(request.question, top_k=3)
        
        # 2. Generate grounded answer
        answer = rag_assistant.generate_answer(request.question, context_docs)
        
        return AskResponse(
            answer=answer,
            context_used=[
                SearchResult(
                    content=res['content'],
                    source=res['metadata']['source'],
                    id=res['metadata']['id'],
                    score=res['score']
                ) for res in context_docs
            ]
        )
    except Exception as e:
        logger.error(f"Ask error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal RAG engine error")

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """Basic Vehicle Recommendation Logic."""
    try:
        results = recommender.recommend(request.needs)
        recommendations = [
            Recommendation(
                model=res['model'],
                score=res['score'],
                reasoning=res['reasoning']
            ) for res in results
        ]
        return RecommendResponse(recommendations=recommendations)
    except Exception as e:
        logger.error(f"Recommend error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal recommendation engine error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
