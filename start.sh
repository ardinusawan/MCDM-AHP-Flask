source $PWD/venv/bin/activate
cd app
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi
