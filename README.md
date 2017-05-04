# MCDM-Docker-with-AHP
* Docker moodle : https://hub.docker.com/r/jhardison/moodle/
* Docker library : http://docker-py.readthedocs.io/en/stable/containers.html
## For the first time
* docker run -d --name DB -p 3306:3306 -e MYSQL_DATABASE=moodle -e MYSQL_ROOT_PASSWORD=moodle -e MYSQL_USER=moodle -e MYSQL_PASSWORD=moodle mysql
* docker run -d -P --name moodle --link DB:DB -e MOODLE_URL=http://localhost:8080 -p 8080:80 jhardison/moodle

### Show all container already installed 
* docker ps -a

# Rev
* Using ubuntu image x 10 container
..* docker run -i -t ubuntu /bin/bash
* https://github.com/MartinThoma/matrix-multiplication
..* ./test.sh -i Testing/100.in -p "python Python/ijkMultiplication.py" -n 100
