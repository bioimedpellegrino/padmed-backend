#!/usr/bin/env bash
#
set -ex
pushd .
BUILD_NUMBER=${BUILD_NUMBER:-local}
DOCKER_COMPOSE_FILES_ROOT="$(dirname $0)/../docker/"

function exiting(){
    popd
}

trap exiting EXIT
trap exiting ERR
cd $DOCKER_COMPOSE_FILES_ROOT
docker-compose up -d

