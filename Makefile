venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3.7 -m venv venv
	. venv/bin/activate; pip3 install  --ignore-installed -Ur requirements.txt
	touch venv/bin/activate

init: venv
	. venv/bin/activate

test: init
	. venv/bin/activate ; python3.7 manage.py test --pattern="*test*" 
	
run: venv
	. venv/bin/activate ; find -iname "*.pyc" -delete; python3.7 manage.py migrate && python3.7 manage.py runserver 0.0.0.0:8000

makemigrations: init
	. venv/bin/activate ; python3.7 manage.py makemigrations

migrate: init
	. venv/bin/activate ; python3.7 manage.py migrate

execute: venv
	. venv/bin/activate; $(command)

createsuperuser: venv
	. venv/bin/activate; python3.7 manage.py createsuperuser

collectstatic: init
	. venv/bin/activate ; python3.7 manage.py collectstatic --noinput

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

startapp: init
	. venv/bin/activate ; python3.7 manage.py startapp $(appname)
#./run-make.sh startapp appname=machine_learning

dumpdata: init
	. venv/bin/activate ; python3.7 manage.py dumpdata --exclude auditlog.logentry --exclude custom_logger --exclude auth.permission --exclude contenttypes --natural-foreign > db.json

loaddata: init
	. venv/bin/activate ; python3.7 manage.py loaddata db.json

delete_logs: init
	. venv/bin/activate ; python3.7 manage.py delete_logs --days $(days) 
#./run-make.sh delete_logs days=30

shell:init
	. venv/bin/activate ; python3.7 manage.py shell

makemessages:init
	. venv/bin/activate ; python3.7 manage.py makemessages -l it --ignore=venv/*

import_config_countries: init
	. venv/bin/activate ; python3.7 manage.py import_config_countries "$(preview)" "$(debug)" "$(local_file_name_with_ext)" "$(language_code)"
#./run-make.sh import_config_countries preview="True" debug="True" local_file_name_with_ext="Elenco-codici-e-denominazioni-al-31_12_2019.csv" language_code="it"

import_dialog_codes: init
	. venv/bin/activate ; python3.7 manage.py import_dialog_codes "$(preview)" "$(local_file_name_with_ext)" "$(language_code)"
#./run-make.sh import_dialog_codes preview="True" local_file_name_with_ext="Country-codes.xls" language_code="en"

.PHONY: clean execute

