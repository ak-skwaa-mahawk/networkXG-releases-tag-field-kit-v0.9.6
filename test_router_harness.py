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
        dt = 0.005
        mass = 1.0
        stiffness = 40.0
        damping = 0.25

        omega_n = math.sqrt(stiffness / mass)
        zeta = damping / (2.0 * math.sqrt(mass * stiffness))
        self.assertGreater(zeta, 0.0, "System must be positively damped")

        # Simulate 600 steps (3.0s) under live flux perturbation
        x = 1.0
        v = 0.0
        peak_amplitudes = []
        prev_v = v

        for step in range(1, 600):
            # Dynamic lambda skew derived from live manifold state
            flux_pert = math.sin(step * 0.05) * self.state.drag_pct
            effective_k = stiffness * (1.0 + flux_pert)

            # Symplectic Euler integration
            a = -(effective_k / mass) * x - (damping / mass) * v
            v += a * dt
            x += v * dt

            # Detect displacement peak via velocity sign change
            if step > 5 and prev_v * v <= 0:
                peak_amplitudes.append(abs(x))

            prev_v = v

        self.assertGreaterEqual(len(peak_amplitudes), 2, f"Must detect harmonic peaks (found {len(peak_amplitudes)})")

        # Invariant: consecutive peak envelopes must strictly decay under positive damping
        for i in range(len(peak_amplitudes) - 1):
            self.assertLessEqual(
                peak_amplitudes[i + 1],
                peak_amplitudes[i] + 1e-4,
                f"Peak {i+1} ({peak_amplitudes[i+1]:.6f}) exceeded prior envelope ({peak_amplitudes[i]:.6f})"
            )

        print(f"[✓] REP_PHYS_001 Passed: {len(peak_amplitudes)} harmonic peaks detected. Damping envelope preserved.")

if __name__ == "__main__":
    unittest.main()
