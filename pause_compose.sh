#!/usr/bin/env bash
for i in $(seq 1 10);
    do
	docker pause moodle$i mariadb$i &
    done
