VENV=venv3
export VENV

ifndef PYTHON
PYTHON=python3.8
export PYTHON
endif

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements3.txt
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate; pip3 install  --ignore-installed -Ur requirements3.txt
	touch $(VENV)/bin/activate

init: venv
	. $(VENV)/bin/activate

test: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py test --pattern="*test*" 
	
run: venv
	. $(VENV)/bin/activate ; find -iname "*.pyc" -delete; $(PYTHON) manage.py migrate && $(PYTHON) manage.py runserver 0.0.0.0:8000

makemigrations: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py makemigrations

migrate: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py migrate

migrate_fake: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py migrate --fake; $(PYTHON) manage.py createcachetable

migrate_one_fake: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py migrate $(appname) ${migration_name} --fake createcachetable

migrate_reverse: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py migrate $(appname) ${migration_name}
	
#./run-make.sh migrate_reverse appname=app migration_name=0001_initial
	
execute: venv
	. $(VENV)/bin/activate; $(command)

createsuperuser: venv
	. $(VENV)/bin/activate; $(PYTHON) manage.py createsuperuser

collectstatic: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py collectstatic --noinput

clean:
	rm -rf $(VENV)
	find -iname "*.pyc" -delete

startapp: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py startapp $(appname)
#./run-make.sh startapp appname=machine_learning

dumpdata: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py dumpdata --exclude auditlog.logentry --exclude custom_logger --exclude auth.permission --exclude contenttypes --natural-foreign > db.json

loaddata: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py loaddata db.json

delete_logs: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py delete_logs --days $(days) 
#./run-make.sh delete_logs days=30

shell:init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py shell

makemessages:init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py makemessages -l it --ignore=$(VENV)/*

import_config_countries: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py import_config_countries "$(preview)" "$(debug)" "$(local_file_name_with_ext)" "$(language_code)"
#./run-make.sh import_config_countries preview="True" debug="True" local_file_name_with_ext="Elenco-codici-e-denominazioni-al-31_12_2019.csv" language_code="it"

import_dialog_codes: init
	. $(VENV)/bin/activate ; $(PYTHON) manage.py import_dialog_codes "$(preview)" "$(local_file_name_with_ext)" "$(language_code)"
#./run-make.sh import_dialog_codes preview="True" local_file_name_with_ext="Country-codes.xls" language_code="en"

.PHONY: clean execute

