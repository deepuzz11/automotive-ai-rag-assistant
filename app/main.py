import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .core.embeddings import engine
from .core.rag import rag_assistant
from .core.recommender import recommender
from .core.intent import classifier
from .models import (
    SearchRequest, SearchResult, 
    AskRequest, AskResponse, 
    RecommendRequest, RecommendResponse, Recommendation
)

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes search engine with localized technical data on startup."""
    logger.info("Initializing Ford Vehicle Intelligence System...")
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        engine.load_data(os.path.join(base_dir, "data"))
    except Exception as e:
        logger.error(f"Initialization failure: {e}")
    yield
    logger.info("System shutdown initiated.")

app = FastAPI(
    title="Ford Vehicle Intelligence System",
    description="Professional RAG-powered knowledge assistant for Ford automotive documentation.",
    version="1.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend Integration
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(base_dir, "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/api/health", tags=["system"])
async def health_check():
    return {"status": "online", "engine": "RAG-EN-V2", "version": "1.2.0"}

@app.post("/search", response_model=list[SearchResult], tags=["retrieval"])
async def search_knowledge(request: SearchRequest):
    """Semantic search across technical manuals and specifications."""
    if not classifier.is_valid_query(request.query):
        return []
    results = engine.search(request.query)
    return [SearchResult(content=res['content'], source=res['metadata']['source'], id=res['metadata']['id'], score=res['score']) for res in results]

@app.post("/ask", response_model=AskResponse, tags=["ai"])
async def ask_assistant(request: AskRequest):
    """Grounded AI responses with intent detection, confidence scoring, and persistent caching."""
    try:
        from .core.database import db_handler
        
        # 1. Intent Detection
        intent_type, default_response = classifier.classify(request.question)
        if intent_type != "informational":
            return AskResponse(answer=default_response, context_used=[], suggestions=classifier.get_follow_up_suggestions(intent_type), intent=intent_type)
            
        # 2. Check Cache
        cached_response = db_handler.get_cached_query(request.question)
        if cached_response:
            logger.info(f"Cache hit for query: {request.question}")
            return AskResponse(**cached_response)

        # 3. Perform RAG
        context_docs = engine.search(request.question, top_k=3)
        avg_score = sum(d['score'] for d in context_docs) / len(context_docs) if context_docs else 0
        answer = rag_assistant.generate_answer(request.question, context_docs)
        
        response = AskResponse(
            answer=answer,
            context_used=[SearchResult(content=res['content'], source=res['metadata']['source'], id=res['metadata']['id'], score=res['score']) for res in context_docs],
            suggestions=classifier.get_follow_up_suggestions("informational"),
            intent="informational",
            confidence=round(avg_score * 100, 1)
        )
        
        # 4. Save to Cache
        db_handler.set_cached_query(request.question, response.dict())
        
        return response
    except Exception as e:
        logger.error(f"Ask Error: {e}")
        raise HTTPException(status_code=500, detail="RAG system fault")

@app.post("/recommend", response_model=RecommendResponse, tags=["matching"])
async def recommend_vehicles(request: RecommendRequest):
    """Attribute-based vehicle recommendation logic."""
    try:
        results = recommender.recommend(request.needs)
        return RecommendResponse(recommendations=[Recommendation(**res) for res in results])
    except Exception as e:
        logger.error(f"Recommend Error: {e}")
        raise HTTPException(status_code=500, detail="Match engine fault")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
