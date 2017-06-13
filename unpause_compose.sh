#!/usr/bin/env bash
for i in $(seq 1 10);
    do
	docker unpause moodle$i mariadb$i &
    done
