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
        """
        if not self.client:
            return "Error: API Key not configured. Please set GROQ_API_KEY in the .env file."

        # Context Injection & Length Control Logic:
        # We concatenate the content of retrieved documents and truncate to avoid LLM overload.
        # Max context length set to ~6000 characters to ensure prompt fits within token limits.
        MAX_CONTEXT_CHARS = 6000
        full_context = "\n---\n".join([doc['content'] for doc in context_documents])
        
        if len(full_context) > MAX_CONTEXT_CHARS:
            logger.warning(f"Context length ({len(full_context)}) exceeds limit. Truncating.")
            full_context = full_context[:MAX_CONTEXT_CHARS] + "... [Context Truncated]"

        # Professional Prompt Template
        prompt = f"""
You are a professional Ford Automotive Assistant. Your goal is to provide accurate, grounded, and helpful information to vehicle owners.

CONTEXT INFORMATION:
{full_context}

USER QUESTION:
{question}

STRICT INSTRUCTIONS:
1. Use ONLY the provided context.
2. DO NOT use phrases like "Based on the provided context" or "According to the records". Answer directly and professionally.
3. If the answer is not in the context, explicitly state that you don't have that specific information and suggest contacting a Ford dealership.
4. For broad questions (e.g., "What vehicles does Ford have?"), summarize the key models and details found in the context into a clear, helpful list.
5. Use bullet points and bold text to highlight specific models, features, or service intervals for high readability.
6. **Follow-up Intelligence**: At the end of every response, suggest one related follow-up question that the user might want to ask (e.g., "Would you like to know the engine specifications for the F-150?" or "Shall I look up the warranty details for this component?").
7. Maintain a helpful, informative AI personality while remaining 100% grounded.

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
            return "I apologize, but I encountered a technical error while connecting to the AI reasoning engine. Please try again later or contact support if the issue persists."

# Singleton instance
rag_assistant = AutomotiveRAG()

