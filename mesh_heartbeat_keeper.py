import urllib.request, json, time, sys

peers = ["HEADSCALE-ALPHA", "HEADSCALE-BETA", "HEADSCALE-GAMMA", "ALPHA", "BETA", "GAMMA"]

print("[*] Mesh heartbeat keeper started (interval: 10s)...", flush=True)
while True:
    for p in peers:
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8080/api/v1/peer/heartbeat",
                data=json.dumps({"peer_id": p}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                pass
        except Exception as e:
            print(f"[!] Error pinging {p}: {e}", file=sys.stderr)
    time.sleep(10.0)
