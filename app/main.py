import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from .core.embeddings import engine
from .core.rag import rag_assistant
from .core.recommender import recommender
from .models import (
    SearchRequest, SearchResult, 
    AskRequest, AskResponse, 
    RecommendRequest, RecommendResponse, Recommendation
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup (data loading, index building) and shutdown tasks.
    """
    logger.info("Initializing Ford Vehicle Intelligence System...")
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        engine.load_data(data_dir)
        logger.info("System initialized successfully.")
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
    
    yield
    
    logger.info("Shutting down Ford Vehicle Intelligence System...")

# Define metadata for tags to ensure clean URLs while maintaining professional display names in Swagger UI
tags_metadata = [
    {
        "name": "system_health",
        "description": "Operations to verify the operational status of the API.",
    },
    {
        "name": "knowledge_retrieval",
        "description": "Semantic search operations across vehicle manuals and technical specifications.",
    },
    {
        "name": "ai_assistant",
        "description": "RAG-based AI interactions providing grounded answers to automotive queries.",
    },
    {
        "name": "vehicle_matching",
        "description": "Logic-based recommendation engine for matching vehicles to user needs.",
    },
]

app = FastAPI(
    title="Ford Vehicle Intelligence System",
    description="""
    Mini AI-Powered Automotive Knowledge Assistant for Ford Vehicles.
    
    Features:
    * **Semantic Search**: Find relevant manual content using FAISS.
    * **RAG Assistant**: Grounded AI answers to vehicle queries.
    * **Vehicle Recommendation**: Logic-based matching for family and utility needs.
    """,
    version="1.1.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

@app.get("/", tags=["system_health"], operation_id="check_health")
async def root():
    """Health check endpoint to verify system status."""
    return {
        "status": "online",
        "system": "Ford Vehicle Intelligence System API",
        "version": "1.1.0"
    }

@app.post("/search", response_model=list[SearchResult], tags=["knowledge_retrieval"], operation_id="search_knowledge")
async def search_knowledge(request: SearchRequest):
    """
    **Semantic Search for Vehicle Knowledge.**
    
    Performs a high-dimensional vector search using FAISS to find technical 
    specifications and manual content relevant to the user query.
    """
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

@app.post("/ask", response_model=AskResponse, tags=["ai_assistant"], operation_id="ask_assistant")
async def ask_assistant(request: AskRequest):
    """
    **RAG-Based Automotive AI Assistant.**
    
    Generates professional, grounded answers about Ford vehicles by 
    augmenting LLM prompts with verified technical context.
    """
    try:
        # 1. Retrieve relevant context (Top-3)
        context_docs = engine.search(request.question, top_k=3)
        
        # 2. Generate grounded answer via LLM
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

@app.post("/recommend", response_model=RecommendResponse, tags=["vehicle_matching"], operation_id="recommend_vehicles")
async def recommend_vehicles(request: RecommendRequest):
    """
    **Attribute-Based Vehicle Recommendations.**
    
    Analyzes user requirements (e.g., towing capacity, family seating) 
    and returns top matching Ford models with logical reasoning.
    """
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
    # Use port 8000 for standard API access
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

