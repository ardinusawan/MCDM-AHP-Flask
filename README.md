# MCDM-Docker-with-AHP
* Docker moodle : https://github.com/bitnami/bitnami-docker-moodle/blob/master/circle.yml
* Moodle username : user
* Moodle password : bitnami

## For the first time
* ./start_compose.sh

### Show all container already installed 
* docker ps -a

# Dependency
* If installing mysqlclient error
..* sudo apt-get install libmysqlclient-dev

# Benchmark
* Using ubuntu image x 10 container
..* docker run -i -t ubuntu /bin/bash
* https://github.com/MartinThoma/matrix-multiplication
..* ./test.sh -i Testing/100.in -p "python Python/ijkMultiplication.py" -n 100

# uWSGI
* https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04
