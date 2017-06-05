#!/usr/bin/env bash
source $PWD/venv/bin/activate
python3 -u $PWD/app/app.py& PID=$!; sleep 3600; kill $PID
#cd app
#uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi
