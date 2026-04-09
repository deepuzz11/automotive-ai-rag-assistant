import os
from groq import Groq
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomotiveRAG:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment.")
        else:
            self.client = Groq(api_key=self.api_key)
            self.model = "llama-3.1-8b-instant"
            
    def generate_answer(self, question, context_documents):
        """Generates a grounded answer based on the provided context."""
        if not self.api_key:
            return "Error: API Key not configured. Please set GROQ_API_KEY."

        context_text = "\n".join([doc['content'] for doc in context_documents])
        
        prompt = f"""
You are a professional Ford Automotive Assistant. Your goal is to provide accurate, grounded, and helpful information to vehicle owners.

CONTEXT INFORMATION:
{context_text}

USER QUESTION:
{question}

STRICT INSTRUCTIONS:
1. Use ONLY the provided context to answer the question.
2. If the answer is not in the context, state that you don't have that specific information and suggest contacting a Ford dealership.
3. Do NOT hallucinate features, specs, or service intervals not mentioned in the context.
4. Keep the tone professional and safety-focused.
5. If the question is about a safety warning, prioritize clear instructions.

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
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API ({type(e).__name__}): {str(e)}")
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"

# Singleton instance
rag_assistant = AutomotiveRAG()
