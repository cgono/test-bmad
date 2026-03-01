#!/usr/bin/env bash
set -euo pipefail

# Python deps (backend)
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"

# Node deps (frontend)
npm ci --prefix frontend
