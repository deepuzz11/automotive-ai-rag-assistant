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
    
    def __init__(self, model_name='all-MiniLM-L6-v2', chunk_size=None, chunk_overlap=None):
        # Explanation of Embeddings:
        # We use 'all-MiniLM-L6-v2', a Sentence-Transformer model that maps 
        # sentences to a 384-dimensional dense vector space. 
        # It is optimized for semantic search and efficient enough for real-time applications.
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Configuration from environment or defaults
        self.chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", 500))
        self.chunk_overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", 50))
        
        logger.info(f"Search Engine initialized with chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
        
    def _chunk_text(self, text: str) -> list[str]:
        """
        Splits text into smaller chunks with overlap to ensure context is preserved.
        This is crucial for long manuals where the relevant information might be 
        buried in a long paragraph.
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= len(text):
                break
            # Move start forward by (chunk_size - overlap)
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks

    def load_data(self, data_dir: str):
        """Loads and prepares documents from synthetic JSON files."""
        files = ['vehicles.json', 'maintenance.json', 'manuals.json']
        
        for file in files:
            path = os.path.join(data_dir, file)
            if not os.path.exists(path):
                logger.warning(f"File {path} not found.")
                continue
                
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if file == 'vehicles.json':
                for item in data:
                    text = f"Model: {item['model']}. Type: {item['type']}. Engine: {item['engine']}. Specs: {item['description']} Features: {', '.join(item['safety_features'])}"
                    chunks = self._chunk_text(text)
                    for chunk in chunks:
                        self.documents.append(chunk)
                        self.metadata.append({"source": file, "id": item['model']})
            
            elif file == 'maintenance.json':
                for item in data:
                    models_str = ", ".join(item.get('applicable_models', []))
                    if 'service' in item:
                        text = f"Service: {item['service']}. Frequency: {item['frequency']}. Details: {item['details']}. Applicable Models: {models_str}"
                        chunks = self._chunk_text(text)
                        for chunk in chunks:
                            self.documents.append(chunk)
                            self.metadata.append({"source": file, "id": item['service']})
                    elif 'warranty' in item:
                        text = f"Warranty: {item['warranty']}. Details: {item['details']}. Applicable Models: {models_str}"
                        chunks = self._chunk_text(text)
                        for chunk in chunks:
                            self.documents.append(chunk)
                            self.metadata.append({"source": file, "id": item['warranty']})
            
            elif file == 'manuals.json':
                for item in data:
                    text = f"Manual Topic: {item['topic']}. Content: {item['content']} Category: {item['category']}"
                    chunks = self._chunk_text(text)
                    for chunk in chunks:
                        self.documents.append(chunk)
                        self.metadata.append({"source": file, "id": item['topic']})
                    
        logger.info(f"Loaded {len(self.documents)} documents.")
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

