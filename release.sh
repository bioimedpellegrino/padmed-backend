#!/bin/bash

# USAGE: ./release.sh branch="master" version="V2.8.5.6" env="dev" site="prodigys"

#!/bin/sh

if [ "$1" == "-h" ]; then
  echo "Usage: `basename $0` branch=\"master\" [version=\"V2.8.5.6\"] env=\"dev\" site=\"prodigys.lab.prodigys.it\""
  exit 1;
fi

BASE_FOLDER=`dirname $0`

branch="master"
env="dev"
version=""
site="prodigys"
reload_path='../..'

for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)   
    case "$KEY" in
            branch)             branch=${VALUE} ;;
            version)            version=${VALUE} ;;
            env)                env=${VALUE} ;;
            site)               site=${VALUE} ;;
            *)   
    esac    
done

# Should always publish from master
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$GIT_BRANCH" != "$branch" ]]; then
  echo "Aborting script, must be on $branch!";
  exit 1;
fi

echo "Branch: $branch"
echo "Base: folder $BASE_FOLDER"
echo "version $version"
echo "env $env"
echo "site $site"

echo "git  or pulling..."
if [ "$version" != "" ] ; then  
   cmd=$(git fetch --tags)
   echo $cmd
   cmd=$(git checkout $version)
   echo $cmd
else
   cmd=$(git fetch)
   echo $cmd
   cmd=$(git pull origin $branch)
   echo $cmd
fi  

if [ "$env" == "production" ] ; then   
    echo "creating symlink"
    cmd=$(ln -sfn $site.env .env)
    echo $cmd

    cmd=$(./run-make.sh collectstatic)
    echo $cmd

    echo "installing requirements and migrate"
    cmd=$(./run-make.sh migrate)
    echo $cmd

    echo "reloading.."
    cmd=$(cd $reload_path)
    echo $cmd
    cmd=$(touch reload)
    echo $cmd

    echo "done"
fi
if [ "$env" == "lab" ] ; then  
    
    echo "creating symlink"
    cmd=$(ln -sfn $site.env .env)
    echo $cmd

    echo "installing requirements and migrate"
    cmd=$(./run-make.sh collectstatic)
    echo $cmd
    
    cmd=$(./run-make.sh migrate)
    echo $cmd

    echo "reloading.."
    cmd=$(sudo service apache2 reload)
    echo $cmd

    echo "done"
fi
if [ "$env" == "dev" ] ; then  

    echo "installing requirements and migrate"
    cmd=$(./run-make.sh migrate)
    echo $cmd

    echo "done"
fi  

exit 1;
