build_image:
	docker build -t git_log_parser:latest .
clean_image:
	docker build -t git_log_parser:latest .
run:
	docker run --rm -ti -v $$PWD:/app git_log_parser:latest bash
run_tmpfs:
	docker run --rm -ti -v $$PWD:/app --mount type=tmpfs,destination=/pgdata git_log_parser:latest
run_attended:
	docker run --rm -ti -v $$PWD:/app --mount type=tmpfs,destination=/pgdata --entrypoint /bin/bash git_log_parser:latest
