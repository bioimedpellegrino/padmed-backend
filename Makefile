venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip3 install  --ignore-installed -Ur requirements.txt
	touch venv/bin/activate

init: venv
	. venv/bin/activate

test: init
	. venv/bin/activate ; python3 manage.py test --pattern="*test*" 
	
run: venv
	. venv/bin/activate ; find -iname "*.pyc" -delete; python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000

makemigrations: init
	. venv/bin/activate ; python3 manage.py makemigrations

migrate: init
	. venv/bin/activate ; python3 manage.py migrate

execute: venv
	. venv/bin/activate; $(command)

createsuperuser: venv
	. venv/bin/activate; python3 manage.py createsuperuser

collectstatic: init
	. venv/bin/activate ; python3 manage.py collectstatic --noinput

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

startapp: init
	. venv/bin/activate ; python3 manage.py startapp $(appname)
#./run-make.sh startapp appname=machine_learning

dumpdata: init
	. venv/bin/activate ; python3 manage.py dumpdata --exclude auditlog.logentry --exclude custom_logger --exclude auth.permission --exclude contenttypes --natural-foreign > db.json

loaddata: init
	. venv/bin/activate ; python3 manage.py loaddata db.json

delete_logs: init
	. venv/bin/activate ; python3 manage.py delete_logs --days $(days) 
#./run-make.sh delete_logs days=30

shell:init
	venv/bin/activate ; python3 manage.py shell


.PHONY: clean execute

