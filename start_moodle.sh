#!/usr/bin/env bash
for i in $(seq 1 10);
    do
	docker start moodle$i mariadb$i &
    done
