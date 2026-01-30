
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- Data Structures ---

@dataclass
class Plant:
    id: str
    name: str
    family_botanical: str
    family_functional: str
    role: str # 'primary', 'secondary', 'support'
    min_percent: float
    max_percent: float
    constraints: Dict[str, Any] = field(default_factory=dict)
    scores: Dict[str, int] = field(default_factory=dict)
    synergies: List[Dict[str, Any]] = field(default_factory=list)
    antagonisms: List[Dict[str, Any]] = field(default_factory=list)
    # Compatibility fields for MVP JSON
    family: str = ""
    attributes: List[str] = field(default_factory=list)
    
    # Dynamic runtime properties
    relevance_score: float = 0.0
    final_role: str = "" # Can change (e.g. Primary -> Secondary)
    final_percent: float = 0.0
    exclusion_reason: Optional[str] = None
    adjustment_reason: Optional[str] = None

@dataclass
class UserProfile:
    priorities: List[str] # e.g. ['anxiety', 'sleep']
    conditions: Dict[str, bool] # e.g. {'pregnancy': True}
    anxiety_level: int = 0
    insomnia_level: int = 0
    stress_level: int = 0

# --- Constraint Engine ---

class ConstraintEngine:
    """
    Enforces the 'RELATIVE DOSING LIMITS.pdf' rules and Phase 2 Antagonisms.
    """
    
    @staticmethod
    def check_safety(plant: Plant, profile: UserProfile) -> bool:
        """Determines if a plant is SAFE to use based on standalone conditions."""
        plant.exclusion_reason = None
        constraints = plant.constraints.get('conditions', [])
        for rule in constraints:
            condition_key = rule.get('condition')
            action = rule.get('action')
            if profile.conditions.get(condition_key, False):
                if action == 'exclude':
                    plant.exclusion_reason = f"Excluded due to {condition_key}"
                    return False
        return True

    @staticmethod
    def check_antagonisms(selected_plants: List[Plant], profile: UserProfile) -> List[Plant]:
        """
        Phase 2: Negative Combinations (Antagonisms).
        Checks pairs and applies penalties or exclusions.
        """
        ids = {p.id for p in selected_plants}
        to_exclude = set()

        for p in selected_plants:
            for ant in p.antagonisms:
                opponent_id = ant.get('with')
                if opponent_id in ids:
                    condition = ant.get('condition')
                    # Evaluate condition if any (simplified parser)
                    triggered = True
                    if condition:
                        if ">=" in condition:
                            key, val = condition.split(">=")
                            key = key.strip()
                            val = int(val.strip())
                            user_val = getattr(profile, f"{key}_level", 0)
                            if user_val < val: triggered = True # Wait, if user_val < val, triggered should be False
                            else: triggered = True
                            if user_val < val: triggered = False
                    
                    if triggered:
                        action = ant.get('action', 'penalize')
                        if action == 'exclude':
                            to_exclude.add(p.id)
                            p.exclusion_reason = f"Antagonism with {opponent_id}"
                        else:
                            penalty = ant.get('penalty', 0)
                            p.relevance_score -= penalty
                            p.adjustment_reason = str(p.adjustment_reason or "") + f" Penalty -{penalty} (antagonism with {opponent_id})"
        
        return [p for p in selected_plants if p.id not in to_exclude]

    @staticmethod
    def apply_conditional_limits(plant: Plant, profile: UserProfile):
        """Adjusts plant.max_percent or plant.role based on conditions."""
        constraints = plant.constraints.get('conditions', [])
        for rule in constraints:
            condition_key = rule.get('condition')
            action = rule.get('action')
            if profile.conditions.get(condition_key, False):
                if action == 'cap_percent':
                    cap = rule.get('value', 100)
                    if plant.max_percent > cap:
                        plant.max_percent = cap
                        plant.adjustment_reason = f"Capped at {cap}% via {condition_key}"
                elif action == 'set_role':
                    new_role = rule.get('value')
                    plant.final_role = new_role
                    plant.adjustment_reason = f"Shifted to {new_role} via {condition_key}"

    @staticmethod
    def validate_family_limits(selected_plants: List[Plant]) -> List[Plant]:
        """Enforces global family caps (e.g. Sedatives <= 40%)."""
        families = {}
        for p in selected_plants:
            fam = p.family_functional
            if fam not in families: families[fam] = []
            families[fam].append(p)
            
        for fam, plants in families.items():
            limit_rule = plants[0].constraints.get('global_family_limit')
            if not limit_rule: continue
            
            max_sum = limit_rule.get('max_sum', 100)
            current_sum = sum(p.final_percent for p in plants)
            
            if current_sum > max_sum:
                ratio = max_sum / current_sum
                for p in plants: p.final_percent *= ratio
        return selected_plants

# --- Main Engine ---

class HerbalFormulator:
    def __init__(self, db_path: str):
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.db = [Plant(**item) for item in data]
        logging.info(f"Loaded {len(self.db)} plants.")

    def generate_formula(self, profile_dict: Dict[str, Any]) -> Dict[str, Any]:
        profile = UserProfile(
            priorities=profile_dict.get('priorities', []),
            conditions=profile_dict.get('conditions', {}).copy(),
            anxiety_level=profile_dict.get('anxiety_level', 0),
            insomnia_level=profile_dict.get('insomnia_level', 0),
            stress_level=profile_dict.get('stress_level', 0)
        )
        
        # Auto-map level thresholds to condition flags per PDF requirements
        if profile.anxiety_level >= 7: profile.conditions['high_anxiety'] = True
        if profile.anxiety_level >= 5: profile.conditions['active_anxiety'] = True
        if profile.insomnia_level >= 7: profile.conditions['insomnia'] = True
        if profile.stress_level >= 7: profile.conditions['high_stress'] = True
        
        # 1. Base Scoring
        scored = self._score_plants(profile)
        
        # 2. Safety Filtering & Conditional Limits
        safe = []
        for p in scored:
            if ConstraintEngine.check_safety(p, profile):
                ConstraintEngine.apply_conditional_limits(p, profile)
                if not p.final_role: p.final_role = p.role
                safe.append(p)
            else:
                logging.info(f"Safety Exclusion: {p.name} - {p.exclusion_reason}")
        
        # 3. Selection (Composition)
        composition_map = self._select_composition(safe, profile)
        # Flatten for formula processing
        selected_plants = []
        for list_p in composition_map.values(): selected_plants.extend(list_p)

        # 4. Phase 2: Apply Synergies and Check Antagonisms on selected set
        selected_plants = self._apply_synergies(selected_plants, profile)
        selected_plants = ConstraintEngine.check_antagonisms(selected_plants, profile)

        # 5. Dosage Calculation
        final_formula = self._calculate_dosages(selected_plants, profile)
        
        return self._format_output(final_formula)

    def _score_plants(self, profile: UserProfile) -> List[Plant]:
        for plant in self.db:
            score = 0
            for prio in profile.priorities:
                score += plant.scores.get(prio, 0)
            plant.relevance_score = float(score)
        return sorted(self.db, key=lambda x: x.relevance_score, reverse=True)

    def _apply_synergies(self, selected: List[Plant], profile: UserProfile) -> List[Plant]:
        """Phase 2: Positive Combinations (Synergies)."""
        ids = {p.id for p in selected}
        for p in selected:
            for syn in p.synergies:
                if syn.get('with') in ids:
                    # Apply bonus
                    bonus = syn.get('bonus', 0)
                    p.relevance_score += bonus
                    p.adjustment_reason = str(p.adjustment_reason or "") + f" Synergy bonus +{bonus}"
        return selected

    def _select_composition(self, ranked_plants: List[Plant], profile: UserProfile) -> Dict[str, List[Plant]]:
        selection = {"primary": [], "secondary": [], "support": []}
        candidates = [p for p in ranked_plants if p.relevance_score > 0]
        
        # Primary (1-2)
        primary_candidates = [p for p in candidates if p.final_role == 'primary']
        if primary_candidates:
            selection['primary'].append(primary_candidates[0])
            if len(primary_candidates) > 1: selection['primary'].append(primary_candidates[1])
                
        # Secondary (2-3)
        secondary_candidates = [p for p in candidates if p.final_role == 'secondary']
        for p in secondary_candidates:
            if len(selection['secondary']) < 3: selection['secondary'].append(p)
        
        # Support (Max 2, Total Max 5)
        support_candidates = [p for p in candidates if p.final_role == 'support']
        for p in support_candidates:
             current_total = sum(len(v) for v in selection.values())
             if current_total < 5 and len(selection['support']) < 2:
                 selection['support'].append(p)

        return selection

    def _calculate_dosages(self, all_plants: List[Plant], profile: UserProfile) -> List[Plant]:
        """Assigns percentages based on roles and constraints."""
        primaries = [p for p in all_plants if p.final_role == 'primary']
        secondaries = [p for p in all_plants if p.final_role == 'secondary']
        supports = [p for p in all_plants if p.final_role == 'support']
        
        if len(primaries) == 1: primaries[0].final_percent = 40.0
        elif len(primaries) == 2:
            for p in primaries: p.final_percent = 30.0
            
        for p in secondaries: p.final_percent = 20.0
        for p in supports: p.final_percent = 10.0
            
        # Apply Caps
        for p in all_plants:
            if p.final_percent > p.max_percent: p.final_percent = p.max_percent

        # Family Limits
        all_plants = ConstraintEngine.validate_family_limits(all_plants)
        
        # Normalize
        total = sum(p.final_percent for p in all_plants)
        if total > 100:
            ratio = 100 / total
            for p in all_plants: p.final_percent *= ratio
        return all_plants

    def _format_output(self, plants: List[Plant]) -> Dict[str, Any]:
        return {
            "total_grams": 4.0,
            "components": [
                {
                    "name": p.name,
                    "role": p.final_role.capitalize(),
                    "percent": round(p.final_percent, 1),
                    "grams": round((p.final_percent / 100) * 4.0, 2),
                    "reason": p.adjustment_reason.strip() if p.adjustment_reason else None
                }
                for p in plants
            ]
        }
