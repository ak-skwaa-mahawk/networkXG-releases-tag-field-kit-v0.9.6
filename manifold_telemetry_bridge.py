"""
manifold_telemetry_bridge.py
Pipes live manifold frames into the continuous lambda-slider routing mechanism.
"""

import asyncio
import socket
import json
import websockets
from cascade_bridge import CascadeState, CascadeEngine, float_to_q32, q32_to_float

async def stream_live_flux(iterations: int = 5):
    uri = "ws://127.0.0.1:8766"
    udp_target = ("127.0.0.1", 9998)
    
    # Initialize state
    state = CascadeState()
    state.phase_pos = int("0x000000010B1D76D1", 16)
    state.scale_omega = int("0x0000000100000000", 16)
    state.depth_k = 0
    state.lambda_slider = float_to_q32(0.5)
    state.drag_pct = 0.002714
    state.centroid_ep_pi = 3.141592653589793

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        async with websockets.connect(uri) as ws:
            print(f"=== STREAMING LIVE FLUX TO LAMBDA-SLIDER ({iterations} ticks) ===")
            for i in range(1, iterations + 1):
                # Stimulate slip listener
                sock.sendto(b"flux_stimulus", udp_target)
                raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                frame = json.loads(raw)
                
                # Extract runtime telemetry flux
                drag = float(frame.get("backpressure_pct", 0.0))
                drive_raw = int(frame.get("drive_input", "0x0"), 16)
                flux_norm = (drive_raw & 0xFFFF) / 65535.0  # normalize [0, 1]
                
                # Skew epsilon-pi centroid dynamically
                prev_lambda = q32_to_float(state.lambda_slider)
                state.drag_pct = drag
                state.lambda_slider = float_to_q32(prev_lambda * 0.9 + flux_norm * 0.1)
                state.centroid_ep_pi = 3.141592653589793 * (1.0 + (flux_norm - 0.5) * drag)
                state.phase_pos = int(frame.get("phase_pos", "0x0"), 16)
                
                print(f"[{i:02d}] Packet: {frame.get('accepted'):<3} | Drag: {drag:.6f}% | "
                      f"λ-Slider: {q32_to_float(state.lambda_slider):.6f} | Centroid ε-π: {state.centroid_ep_pi:.8f}")
                await asyncio.sleep(0.5)
    finally:
        sock.close()

if __name__ == "__main__":
    asyncio.run(stream_live_flux(5))
