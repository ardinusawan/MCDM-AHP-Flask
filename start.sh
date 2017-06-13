#!/usr/bin/env bash
source $PWD/venv/bin/activate
#( cmdpid=$BASHPID; 
#    (sleep 10; kill $cmdpid) \
#   & while ! ping -w 1 www.google.com 
#     do 
#         echo crap; 
#     done )
( cmdpid=$BASHPID; (sleep 21600; kill $cmdpid) & exec python3 -u $PWD/app/app.py )
#python3 -u $PWD/app/app.py& PID=$!; sleep 3600; kill $PID
#cd app
#uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi
