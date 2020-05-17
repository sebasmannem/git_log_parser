#!/bin/bash
for d in /app/git/*/; do
  echo "Processing $d"
  (
  cd "$d" || exit 1
  git log | git_log_commit_parser --path "$PWD"
  )
done
