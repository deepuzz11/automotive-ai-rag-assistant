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

        # Build source citation references
        sources = []
        for i, doc in enumerate(context_documents, 1):
            source_file = doc['metadata']['source'].replace('.json', '').title()
            doc_id = doc['metadata']['id']
            sources.append(f"[{i}] {source_file} — {doc_id}")
        sources_str = "\n".join(sources)

        # Enhanced Professional Prompt Template 
        system_prompt = """You are a senior Ford Automotive Technical Specialist with deep expertise in the full Ford vehicle lineup. You provide precise, actionable, and well-structured answers based exclusively on official Ford documentation.

RESPONSE QUALITY STANDARDS:
- Structure: Always organize your response with clear sections using headers when the answer covers multiple topics.
- Specificity: Include exact numbers, model names, and technical specs whenever available. Never give vague answers like "it has good towing" — say "towing capacity of 13,200 lbs".
- Actionability: When discussing maintenance, include intervals, costs considerations, and what happens if neglected.
- Completeness: Cover all relevant aspects of the question. If asked about a vehicle, touch on engine, capacity, safety, and standout features.
- Comparison: If multiple vehicles are relevant, briefly note how they compare.
- Safety First: Always highlight safety features and warnings when relevant."""

        user_prompt = f"""TECHNICAL CONTEXT (Official Ford Documentation):
{full_context}

SOURCE REFERENCES:
{sources_str}

USER QUESTION:
{question}

STRICT OPERATING CONSTRAINTS:
1. Use ONLY the provided TECHNICAL CONTEXT to answer. Do not use any outside knowledge.
2. If the answer is not in the context, respond: "I don't have that specific information in my current database. Please consult your official Ford Owner's Manual or contact an authorized Ford dealership."
3. Do NOT mention "the context" or "the documents" — answer as the authoritative source.
4. Use this response format:
   - Start with a direct, concise answer to the question (1-2 sentences).
   - Then provide supporting details with specifics (specs, numbers, features).
   - Use bullet points (•) for lists of features or specifications.
   - Use line breaks between sections for readability.
   - End with a relevant safety note or pro-tip if applicable.
5. Keep the tone professional but conversational — like an expert advisor, not a textbook.
6. Reference source numbers like [1], [2] naturally in your answer when citing specific data.

ANSWER:"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                model=self.model,
                temperature=0.15,  # Slightly higher for more natural language while staying grounded
                max_tokens=1024,   # Allow longer, more detailed responses
                top_p=0.9,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            return "I apologize, but I encountered a technical error while connecting to the AI reasoning engine. Please try again later or contact support if the issue persists."

# Singleton instance
rag_assistant = AutomotiveRAG()
