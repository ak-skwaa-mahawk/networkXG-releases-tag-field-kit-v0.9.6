#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=== Starting ISST-TOFT Sovereign Field Kit ==="

# 1. Kill stale instances
killall isst-toft-backend 2>/dev/null || true

# 2. Launch Rust gRPC inference service
echo "[+] Starting Rust gRPC Backend on port 50051..."
./target/release/isst-toft-backend > backend.log 2>&1 &
sleep 1

# 3. Verify socket
if grep -q "listening on \[::\]:50051" backend.log; then
    echo "[✓] Rust Backend active on port 50051."
else
    echo "[!] Check backend.log:"
    cat backend.log
fi

echo "=== Field Kit Ready ==="
