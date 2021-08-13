#!/bin/bash
#
set -e

if [ "${EUID}" -eq 0 ]; then
	echo "Do not run this script as root"
	exit 1
fi

function help(){
  echo -e "This script runs project from local git repo working dir inside a docker environment. The docker image contains a python 3 development ready environment. Local sources folder is mounted inside the container. Please specify an \$ENV_FILE. Usage examples:

 * If you already have a PostgreSQL volume with data to use
      ENV_FILE=<YOUR_ENV_FILE> EXTERNAL_VOLUME_NAME=globalclaims $(basename $0)
 * Custom PostgreSQL docker volume:
      # If you have a SQL dump and want to use it during development you can use the following commands to restore the backup in a volume. Please see example below which restores a backup into a volume namaes dbvolume:

      docker run --name=dbrestore -d -it --rm -v <FOLDER_WITH_BACKUP>:/restore -v dbvolume:/var/lib/postgresql/data -e POSTGRES_DB=<DB_NAME> -e POSTGRES_PASSWORD='<DB_PASSWORD>' -e POSTGRES_USER=<DB_USERNAME> postgres:9.6
      docker exec -it dbrestore bash
      psql -U <DB_NAME> -h localhost -f /restore/<RESTORE_FILE_NAME>
      exit
      docker volume stop dbrestore

      # You can now run the container and specify the desired volume name as EXTERNAL_VOLUME_NAME variable value
      ENV_FILE=<YOUR_ENV_FILE> EXTERNAL_VOLUME_NAME=<YOUR_VOLUME_NAME> $(basename $0)"
}

if [ -z "$ENV_FILE" ]; then
  help
  echo -e "Error: No environmet file given"
  exit 1
fi




GID=65000
PROJECT_SOURCES_BASE_DIR=`dirname $0`
WHOAMI=`whoami`
GROUP_NAME=devgroup
docker volume create project-psql-development-external-vol
sudo groupadd -g 65000 ${GROUP_NAME}|| date # quick hack to make the command always succeed
sudo chown :${GID} ${PROJECT_SOURCES_BASE_DIR}
sudo usermod -a -G ${GROUP_NAME} ${WHOAMI}
chmod 775 ${PROJECT_SOURCES_BASE_DIR}
chmod g+s ${PROJECT_SOURCES_BASE_DIR}


ENV_FILE=${ENV_FILE} ./exec-in-environment.sh docker-compose -f docker/docker-compose.dev.yml up -d
