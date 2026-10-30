#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=== Starting ISST-TOFT Sovereign Field Kit ==="

# 1. Clear stale instances
killall isst-toft-backend 2>/dev/null || true
pkill -f "mesh_heartbeat_keeper.py" 2>/dev/null || true
pkill -f "core.mesh.server" 2>/dev/null || true
sleep 1

# 2. Export Core Environment
export PYTHONPATH="/data/data/com.termux/files/home/Tordial-GS:$PYTHONPATH"
export XRPL_PRODUCTION_WALLET="rwnYLUsoBQX3ECa1A5bSKLdbPoHKnqf63J"
export XRPL_RPC_URL="https://xrplcluster.com"

# 3. Launch Rust gRPC Backend (port 50051)
echo "[+] Starting Rust gRPC Backend..."
nohup ./target/release/isst-toft-backend > backend.log 2>&1 &
sleep 1

# 4. Launch Sovereign Mesh HTTP Gateway (port 8080)
echo "[+] Starting Sovereign Mesh Gateway..."
nohup python3 -u -c "from core.mesh.server import run_server; run_server(port=8080)" > /data/data/com.termux/files/home/Tordial-GS/mesh_server.log 2>&1 &
sleep 2

# 5. Launch Mesh Heartbeat Keeper
echo "[+] Starting Mesh Heartbeat Keeper..."
nohup python3 mesh_heartbeat_keeper.py > heartbeat.log 2>&1 &
sleep 1

# 6. Run Self-Diagnostics
python3 check_system.py

echo "=== Field Kit Active & Sealed ==="
