#!/bin/bash
[ -f /app/csv/vw_committers.csv ] && git_log_committer_csv_parser --path /app/csv/vw_committers.csv
for d in /app/git/*/; do
  echo "Processing $d"
  (
  cd "$d" || exit 1
  git log --stat | git_log_commit_parser --path "$PWD"
  )
done
