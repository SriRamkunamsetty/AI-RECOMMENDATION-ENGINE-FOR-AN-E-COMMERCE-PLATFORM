#!/usr/bin/env bash
set -euo pipefail

python3 -m unittest discover -s tests -v
python3 -m compileall -q .
pyflakes backend components pages state tests
git diff --check

echo "Quality checks passed."
