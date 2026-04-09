import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomotiveSearchEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []
        
    def load_data(self, data_dir):
        """Loads and prepares documents from JSON files."""
        files = ['vehicles.json', 'maintenance.json', 'manuals.json']
        
        for file in files:
            path = os.path.join(data_dir, file)
            if not os.path.exists(path):
                logger.warning(f"File {path} not found.")
                continue
                
            with open(path, 'r') as f:
                data = json.load(f)
                
            if file == 'vehicles.json':
                for item in data:
                    text = f"Model: {item['model']}. Type: {item['type']}. Engine: {item['engine']}. Specs: {item['description']} Features: {', '.join(item['safety_features'])}"
                    self.documents.append(text)
                    self.metadata.append({"source": file, "id": item['model']})
            
            elif file == 'maintenance.json':
                for item in data:
                    if 'service' in item:
                        text = f"Service: {item['service']}. Frequency: {item['frequency']}. Details: {item['details']}"
                        self.documents.append(text)
                        self.metadata.append({"source": file, "id": item['service']})
                    elif 'warranty' in item:
                        text = f"Warranty: {item['warranty']}. Details: {item['details']}"
                        self.documents.append(text)
                        self.metadata.append({"source": file, "id": item['warranty']})
            
            elif file == 'manuals.json':
                for item in data:
                    text = f"Manual Topic: {item['topic']}. Content: {item['content']} Category: {item['category']}"
                    self.documents.append(text)
                    self.metadata.append({"source": file, "id": item['topic']})
                    
        logger.info(f"Loaded {len(self.documents)} documents.")
        self._build_index()

    def _build_index(self):
        """Builds FAISS index from documents."""
        if not self.documents:
            logger.error("No documents to index.")
            return
            
        embeddings = self.model.encode(self.documents, convert_to_numpy=True)
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product on normalized vectors = Cosine Similarity
        self.index.add(embeddings)
        logger.info("FAISS index built successfully.")

    def search(self, query, top_k=3):
        """Searches the index and returns relevant documents and metadata."""
        if self.index is None:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
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
