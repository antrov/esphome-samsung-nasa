#!/usr/bin/env bash
set -euo pipefail

# ESPHome >= 2026.5 is required by samsung_hvac.yaml (esphome: min_version).
python -m pip install --upgrade pip
python -m pip install "esphome>=2026.5"

# The platformio volume is created by Docker as root; hand it to the dev user.
sudo chown -R "$(id -u):$(id -g)" "$HOME/.platformio" 2>/dev/null || true

# secrets.yaml is git-ignored; start from the template.
if [ ! -f secrets.yaml ]; then
  cp secrets.yaml.example secrets.yaml
  echo "Created secrets.yaml from secrets.yaml.example: fill in wifi_ssid and wifi_password."
fi

esphome version
cat <<'EOF'

Usage (see OTA.md):
  esphome config samsung_hvac.yaml                              # validate
  esphome compile samsung_hvac.yaml                             # build
  esphome run samsung_hvac.yaml --device <IP>                   # build + OTA
  esphome run samsung_hvac.yaml --device /dev/ttyUSB0           # build + USB (device must be passed to the container)
  esphome logs samsung_hvac.yaml --device <IP>                  # logs
EOF
