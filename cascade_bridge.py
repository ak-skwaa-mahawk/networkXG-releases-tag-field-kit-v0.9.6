"""
cascade_bridge.py - Direct Ctypes Binding to libcascade.so
Maps Q32.32 fixed-point state, dynamic runtime flux, and epsilon-pi centroid transformations.
"""

import ctypes
import os
from typing import Tuple, List

# Locate libcascade.so across potential compilation targets
SO_CANDIDATES = [
    os.path.join(os.getcwd(), "libcascade.so"),
    os.path.join(os.getcwd(), "target/release/libcascade.so"),
    os.path.join(os.getcwd(), "target/debug/libcascade.so"),
    "/usr/local/lib/libcascade.so"
]

LIB_PATH = next((p for p in SO_CANDIDATES if os.path.exists(p)), None)

# Fixed-point conversion helpers: Q32.32
Q32_SHIFT = 32
Q32_SCALE = 1 << Q32_SHIFT

def float_to_q32(val: float) -> int:
    return int(val * Q32_SCALE) & 0xFFFFFFFFFFFFFFFF

def q32_to_float(val: int) -> float:
    # Handle signed 64-bit wrap
    if val >= (1 << 63):
        val -= (1 << 64)
    return float(val) / Q32_SCALE

class CascadeState(ctypes.Structure):
    _fields_ = [
        ("phase_pos", ctypes.c_uint64),
        ("scale_omega", ctypes.c_uint64),
        ("depth_k", ctypes.c_uint32),
        ("lambda_slider", ctypes.c_uint64),     # Continuous lambda flux threshold
        ("drag_pct", ctypes.c_double),
        ("centroid_ep_pi", ctypes.c_double)     # Epsilon-pi centroid state
    ]

class CascadeEngine:
    def __init__(self, so_path: str = None):
        target = so_path or LIB_PATH
        if not target or not os.path.exists(target):
            raise FileNotFoundError(f"Cannot locate libcascade.so. Searched: {SO_CANDIDATES}")
        
        self.lib = ctypes.CDLL(target)
        self._setup_signatures()

    def _setup_signatures(self):
        # void cascade_init(CascadeState* state, uint64_t initial_lambda)
        if hasattr(self.lib, "cascade_init"):
            self.lib.cascade_init.argtypes = [ctypes.POINTER(CascadeState), ctypes.c_uint64]
            self.lib.cascade_init.restype = None

        # int cascade_step_flux(CascadeState* state, uint64_t flux_in, double backpressure, double* out_deviation)
        if hasattr(self.lib, "cascade_step_flux"):
            self.lib.cascade_step_flux.argtypes = [
                ctypes.POINTER(CascadeState),
                ctypes.c_uint64,
                ctypes.c_double,
                ctypes.POINTER(ctypes.c_double)
            ]
            self.lib.cascade_step_flux.restype = ctypes.c_int

    def step(self, state: CascadeState, flux_val: float, drag: float) -> Tuple[CascadeState, float, int]:
        q32_flux = float_to_q32(flux_val)
        dev = ctypes.c_double(0.0)
        ret = 0
        if hasattr(self.lib, "cascade_step_flux"):
            ret = self.lib.cascade_step_flux(ctypes.byref(state), q32_flux, drag, ctypes.byref(dev))
        else:
            # Fallback pure-python parity calculation if symbol not exported
            state.lambda_slider = float_to_q32(flux_val * (1.0 - drag))
            state.phase_pos = (state.phase_pos + q32_flux) & 0xFFFFFFFFFFFFFFFF
            state.centroid_ep_pi = (flux_val * 3.141592653589793) / (1.0 + drag)
            dev.value = abs(state.centroid_ep_pi - 3.141592653589793)
        return state, dev.value, ret
