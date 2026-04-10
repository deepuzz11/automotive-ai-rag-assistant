import json
import os
import logging
import warnings
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=FutureWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomotiveSearchEngine:
    """
    Core search engine for Ford vehicle knowledge.
    Uses Semantic Search to find relevant manual text blocks and specifications.
    
    Why Semantic Search?
    Unlike keyword search, semantic search understands the context and intent
    behind a query by projecting text into a high-dimensional vector space.
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Explanation of Embeddings:
        # We use 'all-MiniLM-L6-v2', a Sentence-Transformer model that maps 
        # sentences to a 384-dimensional dense vector space. 
        # It is optimized for semantic search and efficient enough for real-time applications.
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        
    def load_data(self, data_dir: str):
        """Loads and prepares documents from the SQLite database."""
        from .database import db_handler
        
        logger.info("Fetching data from SQLite database...")
        
        # 1. Load Vehicles
        vehicles = db_handler.fetch_all_vehicles()
        for item in vehicles:
            text = f"Model: {item['model']}. Type: {item['type']}. Engine: {item['engine']}. Specs: {item['description']} Features: {', '.join(item['safety_features'])}"
            self.documents.append(text)
            self.metadata.append({"source": "database:vehicles", "id": item['model']})
            
        # 2. Load Maintenance & Warranty
        maintenance = db_handler.fetch_all_maintenance()
        for item in maintenance:
            models_str = ", ".join(item.get('applicable_models', []))
            if item['type'] == 'service':
                text = f"Service: {item['title']}. Frequency: {item['frequency']}. Details: {item['details']}. Applicable Models: {models_str}"
            else:
                text = f"Warranty: {item['title']}. Details: {item['details']}. Applicable Models: {models_str}"
            
            self.documents.append(text)
            self.metadata.append({"source": "database:maintenance", "id": item['title']})
            
        # 3. Load Manuals
        manuals = db_handler.fetch_all_manuals()
        for item in manuals:
            text = f"Manual Topic: {item['topic']}. Content: {item['content']} Category: {item['category']}"
            self.documents.append(text)
            self.metadata.append({"source": "database:manuals", "id": item['topic']})
                    
        logger.info(f"Loaded {len(self.documents)} documents from database.")
        self._build_index()

    def _build_index(self):
        """
        Builds FAISS index from document embeddings.
        
        Similarity Metric: Cosine Similarity
        FAISS IndexFlatIP (Inner Product) is used. When vectors are L2-normalized, 
        their dot product is equivalent to their Cosine Similarity.
        This allows us to find the most semantically relevant documents 
        based on the angle between vectors rather than Euclidean distance.
        """
        if not self.documents:
            logger.error("No documents to index.")
            return
            
        embeddings = self.model.encode(self.documents, convert_to_numpy=True, show_progress_bar=False)
        
        # L2-normalization for Cosine Similarity
        faiss.normalize_L2(embeddings)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        logger.info("FAISS index built successfully using Cosine Similarity.")

    def search(self, query: str, top_k: int = 3):
        """
        Searches the FAISS index for the most semantically relevant documents.
        
        Args:
            query: The user's search string.
            top_k: Number of results to retrieve (default is 3 for optimal context/relevance balance).
            
        Returns:
            List of dictionaries containing content, metadata, and similarity score.
        """
        if self.index is None:
            logger.error("Index not initialized. Please load data first.")
            return []
            
        # 1. Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True, show_progress_bar=False)
        
        # 2. IMPORTANT: Explicit L2 Normalization
        # We normalize the query vector to unit length so that the Inner Product
        # search (IndexFlatIP) correctly calculates the Cosine Similarity.
        faiss.normalize_L2(query_embedding)
        
        # 3. Perform search
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            results.append({
                "content": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(distances[0][i])
            })
        return results

# Singleton instance for the app
engine = AutomotiveSearchEngine()

