for i in $(seq 1 10);
    do
	cd ../moodle/$i/
	docker-compose up &
	cd -
    done
