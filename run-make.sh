#!/usr/bin/env bash
#

if [ $# -lt 1 ]
then
	usage="This is a make wrapper that loads env variables from /etc/django/django.env, ~/.django.env, .django.env, \${DJANGO_CONF_ENV_LAST_RESORT} before calling make. Last declared env variable value overrides previous values. Eg: run-make.sh run"
	echo $usage;
	exit -1
fi

pushd .
cd -P -- "$(dirname -- "$0")"


set -o allexport

if [ -f /etc/django/django.env ]
then
    source /etc/django/django.env
fi
if [ -f ~/.django.env ]
then
    source ~/.django.env
fi
if [ -f .django.env ]
then
    source .django.env
fi
if [ -f .env ]
then
    source .env
fi
if [ -f ${DJANGO_CONF_ENV_LAST_RESORT:-""} ]
then
    source ${DJANGO_CONF_ENV_LAST_RESORT}
fi


set +o allexport
make $@
popd
