#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p /workspace
cp "$SCRIPT_DIR/box.scad" /workspace/box.scad
cd /workspace

for part in bottom top hinge_bottom hinge_top; do
    openscad -o "$part.stl" -D "show=\"$part\"" box.scad
done

ls -l bottom.stl top.stl hinge_bottom.stl hinge_top.stl
