#!/usr/bin/env bash
for i in $(seq 1 10);
    do
        cd ./moodle/$i/
        nohup docker rm moodle$i mariadb$i &
        rm -R apache_data/ mariadb_data/ moodle_data/ php_data/
        cd -
    done
