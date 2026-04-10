from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, example="Which Ford SUV has 7 seats?")

class SearchResult(BaseModel):
    content: str
    source: str
    id: str
    score: float

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, example="Service interval for Ford Ranger 2023?")

class AskResponse(BaseModel):
    answer: str
    context_used: List[SearchResult]
    suggestions: List[str] = []
    intent: str = "informational"
    confidence: Optional[float] = None

class RecommendRequest(BaseModel):
    needs: str = Field(..., min_length=1, example="I need a family SUV with lots of space")

class Recommendation(BaseModel):
    model: str
    score: int
    reasoning: str

class RecommendResponse(BaseModel):
    recommendations: List[Recommendation]
