#!/usr/bin/env bash
set -euo pipefail

echo "Installing RustForge CLI..."
chmod +x rustforge-cli

if command -v pip3 >/dev/null 2>&1; then
  pip3 install --user -e . --no-build-isolation 2>/dev/null || pip3 install -e . --no-build-isolation 2>/dev/null || true
fi

echo ""
echo "Ready! Launch RustForge with any of:"
echo "  ./rustforge-cli"
echo "  python3 -m rustforge"
echo "  rustforge   (if ~/.local/bin is on your PATH)"
