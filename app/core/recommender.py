import json
import os

class VehicleRecommender:
    def __init__(self, vehicles_path):
        with open(vehicles_path, 'r') as f:
            self.vehicles = json.load(f)
            
    def recommend(self, user_query):
        """Recommends top 2 vehicles based on user query."""
        query = user_query.lower()
        scored_vehicles = []
        
        for vehicle in self.vehicles:
            score = 0
            reasoning = []
            
            # Keywords mapping
            keywords = {
                "family": ["family", "kids", "seats", "passenger", "space"],
                "towing": ["tow", "towing", "heavy", "hauling", "trailer"],
                "truck": ["truck", "pickup", "bed", "payload"],
                "off-road": ["off-road", "trail", "rough", "ground clearance"],
                "fuel-efficient": ["fuel", "efficient", "mpg", "hybrid", "gas"],
                "sports": ["sports", "fast", "performance", "speed", "v8"],
                "suv": ["suv", "crossover"],
                "city": ["city", "commute", "compact", "parking"]
            }
            
            # Scoring logic
            if any(k in query for k in keywords["family"]):
                if vehicle["seats"] >= 5:
                    score += 2
                    reasoning.append(f"Provides ample seating ({vehicle['seats']} seats) for families.")
                if vehicle["type"] == "SUV":
                    score += 1
            
            if any(k in query for k in keywords["towing"]):
                if vehicle["towing_capacity"] != "N/A":
                    score += 3
                    reasoning.append(f"High towing capacity of {vehicle['towing_capacity']}.")
            
            if any(k in query for k in keywords["truck"]):
                if "Truck" in vehicle["type"]:
                    score += 3
                    reasoning.append("Solid pickup truck build for utility.")
                    
            if any(k in query for k in keywords["sports"]):
                if vehicle["type"] == "Sports Car":
                    score += 5
                    reasoning.append("Iconic sports car performance and V8 power.")
            
            if any(k in query for k in keywords["suv"]):
                if vehicle["type"] == "SUV":
                    score += 3
                    reasoning.append("Versatile SUV body style.")
                    
            if any(k in query for k in keywords["city"]):
                if vehicle["model"] == "Ford Escape":
                    score += 4
                    reasoning.append("Compact size ideal for city navigation and parking.")
            
            # General matching
            if vehicle["model"].lower() in query:
                score += 10
                reasoning.append(f"Directly matches your interest in the {vehicle['model']}.")

            if score > 0:
                scored_vehicles.append({
                    "model": vehicle["model"],
                    "score": score,
                    "reasoning": " ".join(reasoning) if reasoning else "Matches your general requirements."
                })
        
        # Sort by score descending
        scored_vehicles.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 2
        return scored_vehicles[:2]

# Path to data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vehicles.json")
recommender = VehicleRecommender(DATA_PATH)
