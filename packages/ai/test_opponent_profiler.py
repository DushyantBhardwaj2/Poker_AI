import unittest
from packages.ai.opponent_profiler import OpponentProfiler

class TestOpponentProfiler(unittest.TestCase):
    def test_tight_aggressive(self):
        # VPIP 15% (Tight), PFR 10% (Aggression = 10/15 = 66% -> Aggressive)
        result = OpponentProfiler.profile(0.15, 0.10)
        self.assertEqual(result["classification"], "Tight-Aggressive")

    def test_tight_passive(self):
        # VPIP 15% (Tight), PFR 2% (Aggression = 2/15 = 13% -> Passive)
        result = OpponentProfiler.profile(0.15, 0.02)
        self.assertEqual(result["classification"], "Tight-Passive")

    def test_loose_aggressive(self):
        # VPIP 30% (Loose), PFR 20% (Aggression = 20/30 = 66% -> Aggressive)
        result = OpponentProfiler.profile(0.30, 0.20)
        self.assertEqual(result["classification"], "Loose-Aggressive")

    def test_loose_passive(self):
        # VPIP 40% (Loose), PFR 5% (Aggression = 5/40 = 12.5% -> Passive)
        result = OpponentProfiler.profile(0.40, 0.05)
        self.assertEqual(result["classification"], "Loose-Passive")

    def test_clamping(self):
        # Ensure invalid inputs are clamped
        result = OpponentProfiler.profile(1.5, -0.5)
        self.assertEqual(result["vpip"], 1.0)
        self.assertEqual(result["pfr"], 0.0)

if __name__ == '__main__':
    unittest.main()
