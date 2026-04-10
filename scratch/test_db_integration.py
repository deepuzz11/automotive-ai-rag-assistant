import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.core.embeddings import engine
from app.core.recommender import recommender

def test_search():
    print("Testing Search Engine...")
    engine.load_data("data") # This now loads from DB
    results = engine.search("How do I change the oil?")
    for res in results:
        print(f"- {res['metadata']['id']} (Score: {res['score']:.4f})")
    print("\n")

def test_recommend():
    print("Testing Recommender...")
    results = recommender.recommend("I need a family car with lots of seats")
    for res in results:
        print(f"- {res['model']} (Score: {res['score']:.4f}): {res['reasoning']}")
    print("\n")

if __name__ == "__main__":
    test_search()
    test_recommend()
