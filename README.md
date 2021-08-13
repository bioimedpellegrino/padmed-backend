# Django starter Kit

## Dependencies
Django3.X  
at least Python3.6 

## Docker

### DEVELOPMENT

copy .empty.env and create you local .env file

RUN      : ```ENV_FILE=.env ./scripts/run-dev.sh``` 

RUN      : ```CLEAN_VENV=on ENV_FILE=.env ./scripts/run-dev.sh``` 

### Release 

create .env file with the parameters

BUILD    : ```./scripts/build-in-docker-sh```

RUN      : ```./scripts/run-stack.sh``` 

VIEW LOGS: ```cd docker && docker-compose logs -f```

USE      : Browse to http://localhost/


## Native 

Create empty env file with `touch .env`

Create new user `./run-make.sh createsuperuser`

TEST     : ```./run-make.sh test```

RUN      : ```./run-make.sh run``` #Default DB configuration looks for a PostgreSQL db on port 5432 named django. 

USE      : Browse to http://localhost:8000
