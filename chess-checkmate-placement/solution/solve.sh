#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p /workspace/solution
cp "$SCRIPT_DIR/solve.py" /workspace/solution/solve.py
