#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=== Starting ISST-TOFT Sovereign Field Kit ==="

# 1. Clear stale instances
killall isst-toft-backend 2>/dev/null || true
pkill -f "mesh_heartbeat_keeper.py" 2>/dev/null || true

# 2. Launch Rust gRPC backend (port 50051)
echo "[+] Starting Rust gRPC Backend..."
./target/release/isst-toft-backend > backend.log 2>&1 &
sleep 1

# 3. Launch Mesh Heartbeat Keeper
echo "[+] Starting Mesh Heartbeat Keeper..."
python3 mesh_heartbeat_keeper.py > heartbeat.log 2>&1 &
sleep 1

# 4. Verify bindings
if grep -q "listening on \[::\]:50051" backend.log; then
    echo "[✓] Rust Backend active on port 50051."
else
    echo "[!] Check backend.log:"
    cat backend.log
fi

HEALTHY=$(curl -s http://127.0.0.1:8080/health 2>/dev/null | grep -o '"healthy_peers_count": [0-9]*' || echo "failed")
echo "[✓] HTTP Gateway Status: $HEALTHY"

echo "=== Field Kit Active & Sealed ==="
