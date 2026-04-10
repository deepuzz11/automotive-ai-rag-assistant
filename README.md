# Ford Vehicle Intelligence Assistant
## RAG based Automotive Knowledge Assistant

An AI-powered assistant that helps users find information about Ford vehicles, including specifications, maintenance schedules, and technical manuals. The system uses a Retrieval-Augmented Generation (RAG) approach to provide accurate answers based on a structured automotive dataset. It includes semantic search, a chat assistant, and a recommendation tool to match vehicles with user needs.

---

## Simple Overview
- **Chat Assistant**: Answers questions about vehicle specifications and service details.
- **Semantic Search**: Retrieves relevant manual sections using FAISS.
- **Vehicle Matcher**: Recommends models (e.g., Ford F-150, Mustang) based on user needs.
- **Web Interface**: Simple and clean interface to interact with all features.

---

## How It Works

### 1. What is RAG?
RAG (Retrieval-Augmented Generation) is a technique where the system first retrieves relevant information from a dataset and then uses it to generate an answer. This ensures responses are grounded and not based on assumptions.

### 2. Search & Similarity
- **Embeddings**: Text is converted into vectors using the `all-MiniLM-L6-v2` model to capture semantic meaning.
- **Similarity**: Cosine similarity is used to find the most relevant matches from the dataset.

### 3. Hallucination Control
To ensure safety and accuracy, the system is designed to only use retrieved data. If the required information is not available, it returns "I don't know" instead of generating incorrect answers.

---

## Architecture Diagram
<img width="1169" height="827" alt="1 drawio" src="https://github.com/user-attachments/assets/9c5b0b37-028e-4f3b-804a-fe1516959f89" />


## Project Structure
```text
├── app/
│   ├── core/           
│   │   ├── embeddings.py  
│   │   ├── intent.py      
│   │   ├── rag.py         
│   │   └── recommender.py 
│   ├── main.py         
│   └── models.py       
├── frontend/           
├── data/               
├── Dockerfile          
└── requirements.txt    
```

---

## Setup Instructions

### 1. Requirements
- Python 3.10+
- Groq API Key

### 2. Local Run
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GROQ_API_KEY=your_key_here" > .env

# Start server
uvicorn app.main:app --reload
```
Open: [http://localhost:8000](http://localhost:8000)

### 3. Docker Run
```bash
# Build the image
docker build -t ford-ai-assistant .

# Run the container
docker run -p 8000:8000 --env-file .env ford-ai-assistant
```

---

## API Endpoints
- `POST /search` -> Semantic search for documentation
- `POST /ask` -> AI-powered grounded answers (RAG)
- `POST /recommend` -> Vehicle suggestions based on user needs

---

## Goal
To build a simple and reliable AI assistant that helps users quickly access vehicle information without navigating complex manuals, while ensuring accuracy and safety.
