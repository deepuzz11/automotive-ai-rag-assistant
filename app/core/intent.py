import re
import random
from typing import Tuple, List

class IntentClassifier:
    """
    Classifies user query intent to bypass RAG retrieval for non-informational inputs.
    Uses pattern matching with contextual, varied responses for a natural conversational feel.
    """
    
    # Define common greetings with varied, engaging responses
    GREETINGS = {
        "patterns": [
            r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgreetings\b", r"\banybody there\b",
            r"\bwassup\b", r"\bgood morning\b", r"\bgood afternoon\b", r"\bgood evening\b"
        ],
        "responses": [
            "Welcome to the Ford Intelligence System! I'm your dedicated technical specialist. I can help you with:\n\n• Vehicle specifications & comparisons\n• Maintenance schedules & service intervals\n• Safety features & owner's manual topics\n• Vehicle recommendations based on your needs\n\nWhat would you like to explore?",
            "Hello! Ford Intelligence System online and ready. Whether you need specs on the F-150's towing capacity, the Explorer's safety suite, or maintenance guidance — I've got you covered. What can I look up for you?",
            "Hey there! I'm your Ford vehicle intelligence assistant. I have access to detailed specs, maintenance data, and owner's manual content across the full Ford lineup. Fire away with your question!"
        ]
    }
    
    # Define closing/gratitude phrases with warm, varied responses
    CLOSING = {
        "patterns": [
            r"\bthanks\b", r"\bthank you\b", r"\bthx\b", r"\bokay\b", r"\bok\b", 
            r"\bbye\b", r"\bgoodbye\b", r"\bno need\b", r"\bthat's all\b", r"\bnothing else\b",
            r"\bcheers\b", r"\bappreciate\b", r"\bgot it\b", r"\bcool\b"
        ],
        "responses": [
            "Glad I could help! Remember — regular maintenance is the best way to protect your investment. Come back anytime you need Ford vehicle guidance. Drive safe! 🚗",
            "You're welcome! If you ever need specs, maintenance info, or want to compare Ford models, I'm just a message away. Happy driving!",
            "Anytime! Pro tip: bookmark those maintenance intervals I mentioned — staying on schedule can save you thousands down the road. See you next time! 👋"
        ]
    }

    # Handle unclear / very short queries that aren't greetings or closings
    UNCLEAR = {
        "patterns": [
            r"^.{1,2}$",  # 1-2 character messages
            r"^(what|huh|hmm|um|ah|oh|lol|haha|idk|k)\b",
        ],
        "responses": [
            "I'd love to help! Could you be more specific? For example, you could ask:\n\n• \"What's the towing capacity of the Ford F-150?\"\n• \"When should I get an oil change for my Ranger?\"\n• \"Which Ford SUV is best for a family of 7?\"",
            "Not sure I caught that. Try asking me something like:\n\n• \"Tell me about the Ford Explorer's safety features\"\n• \"What engine options does the Mustang have?\"\n• \"Compare the Escape and the Edge\""
        ]
    }

    def __init__(self):
        # Compile patterns for efficiency
        self.greeting_regex = re.compile("|".join(self.GREETINGS["patterns"]), re.IGNORECASE)
        self.closing_regex = re.compile("|".join(self.CLOSING["patterns"]), re.IGNORECASE)
        self.unclear_regex = re.compile("|".join(self.UNCLEAR["patterns"]), re.IGNORECASE)

    def _is_gibberish(self, text: str) -> bool:
        """
        Heuristic to detect keyboard smashes or nonsensical strings.
        """
        if not text: return False
        
        # Split into words
        words = text.split()
        if not words: return False
        
        # Check the first word (often the focus for short typos)
        word = words[0]
        if len(word) < 4: return False
        
        # Check for repeating characters (e.g., "aaaaaaa")
        if re.search(r'(.)\1{3,}', word):
            return True
            
        # Check for lack of vowels in longer words (e.g., "dfgfdgf")
        vowels = re.findall(r'[aeiouy]', word)
        if len(word) > 5 and len(vowels) == 0:
            return True
            
        # Check for high consonant-to-vowel ratio
        if len(word) > 6 and len(vowels) / len(word) < 0.15:
            return True
            
        return False

    def classify(self, query: str) -> Tuple[str, str]:
        """
        Classifies the query and returns (intent_type, default_response).
        
        Returns:
            - ("greeting", response)
            - ("closing", response)
            - ("unclear", response)
            - ("informational", None)
        """
        clean_query = query.strip().lower()
        
        # 1. Check for very short/empty
        if not clean_query:
            return "unclear", random.choice(self.UNCLEAR["responses"])

        # 2. Check for keyboard smashes/gibberish
        if self._is_gibberish(clean_query):
            return "unclear", "I didn't quite catch that. It looks like there might be a typo in your request. Could you please rephrase your question about Ford vehicles?"

        # 3. Check if query matches a greeting
        if self.greeting_regex.search(clean_query) and len(clean_query.split()) <= 3:
            return "greeting", random.choice(self.GREETINGS["responses"])
        
        # 4. Check if query is a closing remark
        if self.closing_regex.search(clean_query) and len(clean_query.split()) <= 4:
            return "closing", random.choice(self.CLOSING["responses"])

        # 5. Check for explicit unclear patterns
        if self.unclear_regex.search(clean_query) and len(clean_query.split()) <= 2:
            return "unclear", random.choice(self.UNCLEAR["responses"])
            
        return "informational", None

    def is_valid_query(self, query: str) -> bool:
        """
        Returns True if the query requires RAG retrieval.
        """
        intent, _ = self.classify(query)
        return intent == "informational"

    def get_follow_up_suggestions(self, intent: str = "informational") -> List[str]:
        """
        Returns context-aware follow-up suggestions based on the detected intent.
        These are actionable queries the user can click to continue the conversation.
        """
        if intent == "greeting":
            return [
                "What is the towing capacity of the Ford F-150?",
                "Which Ford SUV is best for a family of 7?",
                "Tell me about the Mustang's performance specs"
            ]
        elif intent == "closing":
            return [
                "Actually, what's the oil change interval for a Ranger?",
                "One more — compare the Explorer vs Expedition"
            ]
        elif intent == "unclear":
            return [
                "Show me Ford F-150 specs",
                "What maintenance does a Ford Explorer need?",
                "Recommend a Ford for towing a boat"
            ]
        else:
            # Informational follow-ups — rotate to keep it fresh
            pools = [
                [
                    "What are the safety features for this model?",
                    "How does this compare to similar models?",
                    "What's the recommended maintenance schedule?"
                ],
                [
                    "Tell me about the warranty coverage",
                    "What engine options are available?",
                    "What's the towing or payload capacity?"
                ],
                [
                    "Are there any known maintenance tips?",
                    "What are the seating and cargo specs?",
                    "Which trim level offers the best value?"
                ]
            ]
            return random.choice(pools)

# Singleton instance
classifier = IntentClassifier()
