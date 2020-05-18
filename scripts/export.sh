#!/usr/bin/env bash
VIEWS=(vw_committers vw_company_commits vw_repo_velocity)
for vw in "${VIEWS[@]}"; do
  CSVFILE="/app/csv/${vw}.csv"
  echo "Exporting to ${CSVFILE}"
  psql -c "copy (select * from $vw) to '${CSVFILE}' with (format csv);"
done
DUMPFILE="/app/dump/dump_$(date +%s).sql.gz"
echo "Dumping to ${DUMPFILE}"
pg_dump | gzip > "${DUMPFILE}"
