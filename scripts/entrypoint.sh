#!/bin/bash
set -e
mkdir -p /pgdata
chown postgres: /pgdata
su - postgres -c /app/scripts/stage_postgres.sh
su - postgres -c /app/scripts/process_git.sh
