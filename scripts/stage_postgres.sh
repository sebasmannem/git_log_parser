#!/bin/bash
set -e
/usr/pgsql-12/bin/initdb -D /pgdata
/usr/pgsql-12/bin/pg_ctl -D /pgdata start
[ -f /app/scripts/schema.sql ] && cat /app/scripts/schema.sql | psql
