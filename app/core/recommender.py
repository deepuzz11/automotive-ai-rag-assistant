import json
import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleRecommender:
    """
    Logic-based Vehicle Recommendation Engine.
    Matches user needs with vehicle attributes using keyword mapping and scoring.
    
    This tests:
    - Structured thinking
    - Attribute matching
    - Logical filtering
    """
    
    def __init__(self, vehicles_path: str):
        if not os.path.exists(vehicles_path):
            logger.error(f"Vehicles file not found at {vehicles_path}")
            self.vehicles = []
        else:
            with open(vehicles_path, 'r', encoding='utf-8') as f:
                self.vehicles = json.load(f)
            
    def recommend(self, user_query: str) -> list:
        """
        Recommends the top 2 vehicles based on user query intent.
        
        Args:
            user_query: Description of user needs (e.g., "I need a family SUV").
            
        Returns:
            List of dictionaries containing model, score, and reasoning.
        """
        query = user_query.lower()
        scored_vehicles = []
        
        # Keywords mapping for intent detection
        keywords = {
            "family": ["family", "kids", "seats", "passenger", "space", "children"],
            "towing": ["tow", "towing", "heavy", "hauling", "trailer", "boat"],
            "truck": ["truck", "pickup", "bed", "payload", "utility"],
            "off-road": ["off-road", "trail", "rough", "ground clearance", "4x4", "adventure"],
            "fuel-efficient": ["fuel", "efficient", "mpg", "hybrid", "gas", "electric", "eco"],
            "sports": ["sports", "fast", "performance", "speed", "v8", "racing"],
            "suv": ["suv", "crossover", "wagon"],
            "city": ["city", "commute", "compact", "parking", "small"]
        }
        
        for vehicle in self.vehicles:
            score = 0
            reasoning = []
            
            # 1. Family Intent Matching
            if any(re.search(rf'\b{k}\b', query) for k in keywords["family"]):
                if vehicle.get("seats", 0) >= 5:
                    score += 2
                    reasoning.append(f"Provides ample seating ({vehicle['seats']} seats) for families.")
                if vehicle["type"] == "SUV":
                    score += 1
            
            # 2. Towing Intent Matching
            if any(re.search(rf'\b{k}\b', query) for k in keywords["towing"]):
                if vehicle.get("towing_capacity") != "N/A":
                    score += 3
                    reasoning.append(f"High towing capacity of {vehicle['towing_capacity']}.")
            
            # 3. Utility/Truck Intent Matching
            if any(re.search(rf'\b{k}\b', query) for k in keywords["truck"]):
                if "Truck" in vehicle["type"]:
                    score += 4
                    reasoning.append("Solid pickup truck build for utility and payload.")
                    
            # 4. Performance Intent Matching
            if any(re.search(rf'\b{k}\b', query) for k in keywords["sports"]):
                if "Sports" in vehicle["type"]:
                    score += 5
                    reasoning.append("Iconic performance and high-output engine.")
            
            # 5. Body Style Matching (SUV)
            if any(re.search(rf'\b{k}\b', query) for k in keywords["suv"]):
                if "SUV" in vehicle["type"]:
                    score += 3
                    reasoning.append("Versatile SUV body style with high driving position.")
            
            # 6. City/Efficiency Intent Matching
            if any(re.search(rf'\b{k}\b', query) for k in keywords["city"]):
                if vehicle["model"] in ["Ford Escape", "Ford Maverick"]:
                    score += 4
                    reasoning.append("Compact dimensions ideal for city navigation and parking.")
            
            # 7. Specific Model Mention
            if vehicle["model"].lower() in query:
                score += 10
                reasoning.append(f"Direct match for your interest in the {vehicle['model']}.")

            if score > 0:
                scored_vehicles.append({
                    "model": vehicle["model"],
                    "score": score,
                    "reasoning": " ".join(reasoning) if reasoning else "Matches your general lifestyle requirements."
                })
        
        # Sort by score descending
        scored_vehicles.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 2 as required by assessment
        return scored_vehicles[:2]

# Initialize Recommender
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vehicles.json")
recommender = VehicleRecommender(DATA_PATH)

