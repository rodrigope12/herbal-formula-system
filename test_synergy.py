
import sys
import os
sys.path.append('/Users/rodrigoperezcordero/Documents/TRABAJO')
from herbal_engine import HerbalFormulator

def run_tests():
    formulator = HerbalFormulator('/Users/rodrigoperezcordero/Documents/TRABAJO/plants_db.json')
    
    print("\n--- Test 1: Synergy (Valerian + Passionflower) ---")
    profile_synergy = {
        "priorities": ["sleep", "anxiety"],
        "conditions": {},
        "anxiety_level": 5
    }
    formula = formulator.generate_formula(profile_synergy)
    has_synergy = False
    for comp in formula['components']:
        print(f"{comp['name']}: {comp['percent']}% - Reason: {comp['reason']}")
        if comp['reason'] and "Synergy bonus" in comp['reason']:
            has_synergy = True
    print(f"Synergy Detected: {has_synergy}")

    print("\n--- Test 2: Antagonism Restriction (Anxiety 6, Penalty) ---")
    profile_penalty = {
        "priorities": ["energy", "focus", "anxiety"],
        "conditions": {},
        "anxiety_level": 6
    }
    formula = formulator.generate_formula(profile_penalty)
    has_penalty = False
    for comp in formula['components']:
        print(f"{comp['name']}: {comp['percent']}% - Reason: {comp['reason']}")
        if comp['reason'] and "Penalty" in comp['reason']:
            has_penalty = True
    print(f"Penalty Detected: {has_penalty}")

    print("\n--- Test 3: Antagonism Exclusion (Anxiety 7, Exclusion) ---")
    profile_exclude = {
        "priorities": ["energy", "focus", "anxiety"],
        "conditions": {},
        "anxiety_level": 7
    }
    formula = formulator.generate_formula(profile_exclude)
    # Ginseng should be hard-excluded by standalone condition anyway at 7, 
    # but let's see if Green Tea is kept and Ginseng is gone.
    names = [c['name'] for c in formula['components']]
    print(f"Selected: {names}")
    if "Korean Ginseng" not in names:
        print("Success: Korean Ginseng excluded (safety or antagonism)")

if __name__ == "__main__":
    run_tests()
