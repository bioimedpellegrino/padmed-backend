#!/usr/bin/env bash
#
set -ex
pushd .
BUILD_NUMBER=${BUILD_NUMBER:-local}
DOCKER_COMPOSE_FILES_ROOT="$(dirname $0)/../docker/"

function stop_containers(){
    docker-compose down    
    popd
}
trap stop_containers EXIT
trap stop_containers ERR
cd $DOCKER_COMPOSE_FILES_ROOT
if [ "x${SKIP_TESTS}" = "xtrue" ]; then
  docker-compose build web
else
    
  docker-compose -f docker-compose.yml -f docker-compose.test.yml build web-test && docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm web-test && docker-compose build web
fi
