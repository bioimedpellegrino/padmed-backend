#!/bin/bash

#e.g. ./build.sh major
#     ./build.sh minor

if [ "$1" == "-h" ]; then
  echo "Usage: `basename $0` [major, minor, revision, buildNumber]"
  exit 1;
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "master" ]]; then
  echo 'Aborting script, must be master!';
  exit 1;
fi

 cmd=$(git fetch)
 echo $cmd

 cmd=$(git pull origin master)
 echo $cmd

 cmd=$(git merge origin/development)
 echo $cmd

 VERSION_MODE=$1  
 ENV_TAG_PREFIX=V
#  "major": 1,  
#  "minor": 0,  
#  "revision": 0,  
#  "buildNumber": 1  
 if [ "$VERSION_MODE" = "" ] ; then  
      VERSION_MODE="buildNumber"  
 fi  
 #cd /path/to/your/git/checkout  
 #get highest tag number  
 VERSION=`git describe --match "$ENV_TAG_PREFIX[0-9]*" --abbrev=0 --tags`  
 #replace . with space so can split into an array  
 VERSION_BITS=(${VERSION//./ })  
 #get number parts and increase last one by 1  
 VNUM1=${VERSION_BITS[0]}  
 if [ "$VNUM1" = "" ] ; then  
      VNUM1=0;  
 fi  
 VNUM2=${VERSION_BITS[1]}  
 if [ "$VNUM2" = "" ] ; then  
      VNUM2=0;  
 fi  
 VNUM3=${VERSION_BITS[2]}  
 if [ "$VNUM3" = "" ] ; then  
      VNUM3=0;  
 fi  
 VNUM4=${VERSION_BITS[3]}  
 if [ "$VNUM4" = "" ] ; then  
      VNUM4=0;  
 fi  
 case $VERSION_MODE in  
       "major")  
           VNUM1=$((VNUM1+1))  
           VNUM2=0
           VNUM3=0
           VNUM4=0
           ;;  
      "minor")  
           VNUM2=$((VNUM2+1)) 
           VNUM3=0
           VNUM4=0 
           ;;  
      "revision")  
           VNUM3=$((VNUM3+1))  
           VNUM4=0
           ;;  
     "buildNumber" )  
           VNUM4=$((VNUM4+1))  
           ;;  
 esac  
 #create new tag  
 NEW_TAG="$VNUM1.$VNUM2.$VNUM3.$VNUM4"  
 echo "Last tag version $VERSION New tag will be $NEW_TAG"  
 #get current hash and see if it already has a tag  

 
 echo "$NEW_TAG" > templates/version.html

 echo "updated version.html $NEW_TAG" 

 cmd=$(git add -A)
 echo $cmd

 cmd=$(git commit -m "auto: build" )
 echo $cmd

 cmd=$(git push origin master)
 echo $cmd

  GIT_COMMIT=`git rev-parse HEAD`  
 NEEDS_TAG=`git describe --contains $GIT_COMMIT 2>/dev/null`  

 echo "###############################################################"  
 #only tag if no tag already (would be better if the git describe command above could have a silent option)  
 if [ -z "$NEEDS_TAG" ]; then  
   echo "Tagged with $NEW_TAG (Ignoring fatal:cannot describe - this means commit is untagged) "  
   git tag -a $NEW_TAG -m "$VERSION_MODE"  
   git push --tags  
 else  
   echo "Current commit already has a tag $VERSION"  
 fi  
 echo "###############################################################"  

 cmd=$(git checkout development)
 echo $cmd


# Only show most recent tag without trailing commit information



