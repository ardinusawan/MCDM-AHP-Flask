#!/usr/bin/env bash
for i in $(seq 1 10);
    do
        nohup docker rm moodle$i &
    done
