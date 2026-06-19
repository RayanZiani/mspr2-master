#!/bin/bash
# Dépendances système Chromium pour Playwright (Debian/Ubuntu).
# N'utilise pas "playwright install-deps" : échoue sur Debian Trixie (paquets fonts obsolètes).
set -euo pipefail

if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get indisponible — dépendances Playwright supposées dans l'image Jenkins"
  exit 0
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y --no-install-recommends \
  libglib2.0-0 \
  libnss3 \
  libnspr4 \
  libdbus-1-3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libatspi2.0-0 \
  libcups2 \
  libdrm2 \
  libx11-6 \
  libxcomposite1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libxcb1 \
  libxkbcommon0 \
  libpango-1.0-0 \
  libcairo2 \
  libasound2 \
  fonts-liberation \
  fonts-unifont \
  ca-certificates

rm -rf /var/lib/apt/lists/*
echo "Dépendances Playwright installées."
