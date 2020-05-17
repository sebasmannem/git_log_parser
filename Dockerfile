FROM fedora:latest
RUN dnf install -y git glibc-langpack-en && \
    dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/F-32-x86_64/pgdg-fedora-repo-latest.noarch.rpm && \
    dnf update -y && \
    dnf install -y --repo pgdg12 --repo fedora python3-pip postgresql12-server && \
    pip install psycopg2-binary
COPY scripts/* /app/scripts/
COPY git_log_parser /app/git_log_parser
RUN pip3 install /app/git_log_parser/
ENTRYPOINT /app/scripts/entrypoint.sh
