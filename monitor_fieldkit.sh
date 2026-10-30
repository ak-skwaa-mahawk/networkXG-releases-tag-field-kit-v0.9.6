#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=== $(date -u +"%Y-%m-%d %H:%M:%S UTC") ===
[*] Checking field kit services..."
PORTS=(8080 50051 8766 50055)
MISSING=0

for PORT in "${PORTS[@]}"; do
    if ! python3 -c "import socket; s = socket.socket(); exit(s.connect_ex(('127.0.0.1', $PORT)))" 2>/dev/null; then
        echo "[!] Port $PORT down."
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "[+] Restarting services via start_fieldkit.sh..."
    ./start_fieldkit.sh
else
    echo "[✓] All operational planes nominal."
fi
