#!/usr/bin/env bash
set -euo pipefail

# ship.sh — commit and push current work to GitHub.

if [ -z "$(git status --porcelain)" ]; then
    echo "Nothing to commit."
    exit 0
fi

git add -A

read -rp "Commit message: " msg

git commit -m "$msg"
git push