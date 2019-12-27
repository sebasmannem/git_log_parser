#!/bin/bash
for d in /app/git/*/; do
  echo "Processing $d"
  cd "$d"
  git log | python3 /app/scripts/git_log_parser.py --path "$PWD"
done
