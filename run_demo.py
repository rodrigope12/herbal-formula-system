from herbal_engine import HerbalFormulator
import json

def run_demo():
    print("--- Personal Herbal Formula Generator (Prototype) ---")
    
    # Initialize Engine
    engine = HerbalFormulator("/Users/rodrigoperezcordero/Documents/TRABAJO/plants_db.json")
    
    # 3 Test Cases from User Requirements
    test_cases = [
        {
            "id": 1,
            "name": "User A (Insomnia & Anxiety)",
            "priorities": ["sleep", "anxiety"],
            "pregnancy": False,
            "medications": False,
            "high_anxiety": True
        },
        {
            "id": 2,
            "name": "User B (Focus & Energy, High Anxiety)",
            "priorities": ["focus", "energy"],
            "pregnancy": False,
            "medications": False,
            "high_anxiety": True # Should exclude stimulants like Green Tea depending on logic
        },
        {
            "id": 3,
            "name": "User C (Digestion, Pregnancy)",
            "priorities": ["digestion", "bloating"],
            "pregnancy": True, # Should exclude contraindicated plants
            "medications": False,
            "high_anxiety": False
        }
    ]
    
    for case in test_cases:
        print(f"\nGenerando Formula para: {case['name']}...")
        formula = engine.generate_formula(case)
        
        print("Formula Result:")
        for component in formula['components']:
            grams = (component['percent'] / 100) * 4.0
            print(f"  - {component['name']} ({component['role']}): {component['percent']}% (~{grams:.1f}g)")
        print("-" * 30)

if __name__ == "__main__":
    run_demo()
