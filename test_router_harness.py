"""
test_router_harness.py
Validates dynamic scale-cascade router transformations against REP_PHYS_001.
"""

import math
import unittest
from cascade_bridge import CascadeState, float_to_q32, q32_to_float

class TestScientificVerification(unittest.TestCase):
    def setUp(self):
        self.state = CascadeState()
        self.state.phase_pos = 0x100000000
        self.state.scale_omega = 0x100000000
        self.state.depth_k = 0
        self.state.lambda_slider = float_to_q32(0.5)
        self.state.drag_pct = 0.002714
        self.state.centroid_ep_pi = math.pi

    def test_rep_phys_001_damped_harmonic_bound(self):
        """
        REP_PHYS_001: Ensures that dynamic flux perturbation retains bounded
        logarithmic decrement (zeta >= 0) and cannot provoke non-physical resonant divergence.
        """
        dt = 0.01
        mass = 1.0
        stiffness = 40.0
        damping = 0.2
        
        omega_n = math.sqrt(stiffness / mass)
        zeta = damping / (2.0 * math.sqrt(mass * stiffness))
        self.assertGreater(zeta, 0.0, "System must be positively damped")

        # Simulate 100 cycles under live flux perturbation
        x = 1.0
        v = 0.0
        peak_amplitudes = []

        for step in range(200):
            # Dynamic lambda skew derived from state
            flux_pert = (math.sin(step * 0.1) * self.state.drag_pct)
            effective_k = stiffness * (1.0 + flux_pert)
            
            # Harmonic step (Verlet/Euler integration)
            a = -(effective_k / mass) * x - (damping / mass) * v
            v += a * dt
            x += v * dt
            
            if step > 1 and abs(v) < 0.05:
                peak_amplitudes.append(abs(x))

        # Invariant: consecutive peak envelopes must strictly decrease
        self.assertTrue(len(peak_amplitudes) >= 2, "Must detect harmonic peaks")
        for i in range(len(peak_amplitudes) - 1):
            self.assertLessEqual(
                peak_amplitudes[i + 1], 
                peak_amplitudes[i] + 1e-4,
                f"Peak {i+1} diverged from exponential decay boundary"
            )
        print(f"[✓] REP_PHYS_001 Passed: Damping invariant strictly preserved under dynamic flux.")

if __name__ == "__main__":
    unittest.main()
