import os
import logging
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomotiveRAG:
    """
    RAG-Based Automotive Assistant.
    Combines information retrieval with LLM generation to provide grounded answers.
    
    Hallucination Mitigation Strategy:
    1. Strict Grounding: The prompt explicitly forbids the LLM from using external knowledge.
    2. Fallback Mechanism: LLM is instructed to say "I don't know" if context is insufficient.
    3. Safety Focus: Prioritizes official maintenance schedules and safety warnings.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. AI Assistant functionality will be limited.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
            self.model = "llama-3.1-8b-instant"
            logger.info(f"AutomotiveRAG initialized with model: {self.model}")
            
    def generate_answer(self, question: str, context_documents: list) -> str:
        """
        Generates a grounded answer based on the retrieved context.
        
        Args:
            question: The user's query.
            context_documents: List of relevant document chunks from the search engine.
            
        Returns:
            A string containing the LLM-generated answer.
        """
        if not self.client:
            return "Error: API Key not configured. Please set GROQ_API_KEY in the .env file."

        # Context Injection Logic:
        # We concatenate the content of retrieved documents into a single context block.
        context_text = "\n---\n".join([doc['content'] for doc in context_documents])
        
        # Professional Prompt Template
        prompt = f"""
You are a professional Ford Automotive Assistant. Your goal is to provide accurate, grounded, and helpful information to vehicle owners.

CONTEXT INFORMATION:
{context_text}

USER QUESTION:
{question}

STRICT INSTRUCTIONS:
1. Use ONLY the provided context to answer the question.
2. If the answer is not in the context, explicitly state that you don't have that specific information in your records and suggest contacting a Ford dealership for the most accurate advice.
3. Do NOT hallucinate features, specs, or service intervals not mentioned in the context.
4. Keep the tone professional, concise, and safety-focused.
5. If the question is about a safety warning or dashboard light, prioritize clear, actionable instructions.

ANSWER:
"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.1, # Low temperature for more deterministic/grounded output
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            return "I apologize, but I encountered a technical error while processing your request. Please try again later."

# Singleton instance
rag_assistant = AutomotiveRAG()

