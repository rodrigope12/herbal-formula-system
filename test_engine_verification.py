
import unittest
from herbal_engine import HerbalFormulator, Plant, UserProfile

class TestHerbalEngine(unittest.TestCase):
    def setUp(self):
        # Using the actual generated file to ensure integration correctness
        self.engine = HerbalFormulator("/Users/rodrigoperezcordero/Documents/TRABAJO/plants_db.json")

    def test_global_family_limit(self):
        """Verify Sedatives do not exceed 40%"""
        profile = {
            "priorities": ["sleep", "anxiety"],
            "conditions": {},
            "anxiety_level": 8,
            "insomnia_level": 8
        }
        result = self.engine.generate_formula(profile)
        
        # Calculate total sedative percent
        sedative_sum = 0
        for c in result['components']:
            # Find plant object to check family
            original = next((p for p in self.engine.db if p.name == c['name']), None)
            if original and original.family_functional == "Sedative":
                sedative_sum += c['percent']
        
        # Allow small float error
        self.assertLessEqual(sedative_sum, 40.1, f"Sedatives totaled {sedative_sum}%, violating 40% limit")

    def test_green_tea_cap(self):
        """Verify Green Tea never exceeds 15% even if it's the only priority"""
        profile = {
            "priorities": ["energy", "focus"],
            "conditions": {},
            "anxiety_level": 0
        }
        result = self.engine.generate_formula(profile)
        
        gt = next((c for c in result['components'] if c['name'] == "Green Tea"), None)
        if gt:
            self.assertLessEqual(gt['percent'], 15.1)

    def test_korean_ginseng_exclusion_anxiety(self):
        """Verify Korean Ginseng is excluded if anxiety >= 7"""
        profile_high_anxiety = {
            "priorities": ["energy"],
            "conditions": {"high_anxiety": True, "anxiety_level": 8}
        }
        res = self.engine.generate_formula(profile_high_anxiety)
        names = [c['name'] for c in res['components']]
        self.assertNotIn("Korean Ginseng", names)

    def test_daytime_anxiety_limits(self):
        """Verify Valerian is capped/limited for daytime anxiety"""
        # Logic: daytime_anxiety active
        profile = {
            "priorities": ["anxiety"],
            "conditions": {"daytime_anxiety": True},
            "anxiety_level": 6,
            "insomnia_level": 2
        }
        res = self.engine.generate_formula(profile)
        valerian = next((c for c in res['components'] if c['name'] == "Valerian"), None)
        
        if valerian:
            # Should be capped at 25% or Role switched to secondary (max 20)
            self.assertLessEqual(valerian['percent'], 25.1)

if __name__ == '__main__':
    unittest.main()
