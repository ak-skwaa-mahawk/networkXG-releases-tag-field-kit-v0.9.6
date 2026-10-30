import urllib.request, json, grpc, asyncio, websockets, socket

print("=== SOVEREIGN FIELD KIT: LIVE STATUS ===")

# 1. Edge & Mesh Peer Health
try:
    with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=2) as r:
        h = json.loads(r.read().decode())
        print(f"[✓] Node: {h.get('node_id')} | Status: {h.get('status')} | Peers: {h.get('healthy_peers_count')}/6")
except Exception as e:
    print(f"[✗] Edge Gateway: {e}")

# 2. Rust Candle gRPC Engine
try:
    import inference_pb2, inference_pb2_grpc
    ch = grpc.insecure_channel("localhost:50051")
    stub = inference_pb2_grpc.InferenceServiceStub(ch)
    r = stub.EncodeRadHardGlyph(inference_pb2.GlyphRequest(terrain_data=[3.204423, 7.83], use_agentic=True), timeout=2.0)
    print(f"[✓] gRPC Backend: {r.status} | Coherence: {r.coherence:.2f}% | Checksum: {r.waveform_checksum}")
    ch.close()
except Exception as e:
    print(f"[✗] gRPC: {e}")

# 3. Telemetry Stream
async def probe_telemetry():
    try:
        async with websockets.connect("ws://127.0.0.1:8766") as ws:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"ping", ("127.0.0.1", 9998))
            s.close()
            t = json.loads(await asyncio.wait_for(ws.recv(), timeout=2.0))
            print(f"[✓] Telemetry WS: Phase {t.get('phase_pos')} | Packets: {t.get('accepted')} | Drag: {t.get('backpressure_pct'):.6f}%")
    except Exception as e:
        print(f"[✗] Telemetry WS: {e}")

asyncio.run(probe_telemetry())
print("=========================================")
