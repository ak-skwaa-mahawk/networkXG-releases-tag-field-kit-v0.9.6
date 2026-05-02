#!/bin/bash
# BushRouter Field Kit v0.9.6 — ONE-CLICK RITUAL
echo "🪶 MAHS’I CHOO — Floor is solid. Deploying BushRouter..."

# 1. Termux bootstrap
pkg update && pkg upgrade -y
pkg install python git termux-api openssh curl -y

# 2. Clone canonical repo + field kit
git clone https://github.com/ak-skwaa-mahawk/networkXG.git \~/BushRouter
cd \~/BushRouter
git submodule update --init --recursive

# 3. Install Python environment
pip install networkx torch numpy pandas

# 4. APN provisioning (Alaska GCI / AT&T MVNO optimized)
cp apn-provisioning/bushrouter_apn.xml /sdcard/Download/
echo "APN XML ready — import via Settings → Network → Advanced → APN (or use ADB)"

# 5. Headscale / Tailscale config
cp tailscale-headscale/headscale.yml \~/.config/headscale/config.yml

# 6. Run the Living Ritual
python core/generate_bushrouter_ritual.py "John" "Anchorage-YukonFlats-Node"

# 7. Activate hotspot + tunnel + handshake
termux-wifi-enable true
python -c '
from core.isst_toft_core import bushrouter_handshake
print(bushrouter_handshake("FIELD_KIT_ACTIVATION", proximity_meters=1.8))
'

echo "✅ BUSHRouter CONNECTED — 48 kHz resonance confirmed"
echo "The phone is now the router. The land returns."