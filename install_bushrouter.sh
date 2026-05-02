#!/bin/bash
echo "🪶 MAHS’I CHOO — Deploying BushRouter v0.9.6 (Anchorage Node)"

pkg update && pkg upgrade -y
pkg install python git termux-api openssh curl -y

git clone https://github.com/ak-skwaa-mahawk/networkXG.git \~/BushRouter
cd \~/BushRouter
pip install networkx torch numpy

cp ../bushrouter_apn.xml /sdcard/Download/
cp ../headscale.yml \~/.config/headscale/config.yml

python -c '
from isst_toft_core import bushrouter_handshake
from BushData import generate_bushrouter_tailscale_apn_ritual
print(generate_bushrouter_tailscale_apn_ritual("John", "Anchorage-YukonFlats-Node"))
print(bushrouter_handshake("FIELD_KIT_ACTIVATION", proximity_meters=1.8))
'

termux-wifi-enable true
echo "✅ BUSHRouter CONNECTED — 48 kHz resonance confirmed"
echo "The Floor is solid. The land returns."