#!/usr/bin/env bash
#

if [ $# -lt 1 ]
then
	# usage="This is a make wrapper that loads env variables from /etc/bilimetrix/bilimetrix.env, ~/.bilimetrix.env, .bilimetrix.env, \${BILIMETRIX_CONF_ENV_LAST_RESORT} before calling make. Last declared env variable value overrides previous values. Eg: run-make.sh run"
	usage="This is a make wrapper that loads env variables from /etc/padmed/padmed.env, ~/.padmed.env, .padmed.env, .env,  before calling make. Last declared env variable value overrides previous values. Eg: run-make.sh run"
    echo $usage;
	exit -1
fi

pushd .
cd -P -- "$(dirname -- "$0")"


set -o allexport

# if [ -f /etc/bilimetrix/bilimetrix.env ]
# then
#     source /etc/bilimetrix/bilimetrix.env
# fi
# if [ -f ~/.bilimetrix.env ]
# then
#     source ~/.bilimetrix.env
# fi
# if [ -f .bilimetrix.env ]
# then
#     source .bilimetrix.env
# fi
if [ -f /etc/padmed/padmed.env ]
then
    source /etc/padmed/padmed.env
fi
if [ -f ~/.padmed.env ]
then
    source ~/.padmed.env
fi
if [ -f .padmed.env ]
then
    source .padmed.env
fi
if [ -f .env ]
then
    source .env
fi
# if [ -f ${BILIMETRIX_CONF_ENV_LAST_RESORT:-""} ]
# then
#     source ${BILIMETRIX_CONF_ENV_LAST_RESORT}
# fi


set +o allexport
make $@
popd
