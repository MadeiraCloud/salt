#!/bin/bash
#
## by Thibault BRONCHAIN
## (c) 2014 MadeiraCloud LTD.
#

DEFAULT_TAG="v2014-07-18"

# get tag
echo "Input the tag you want to publish [${DEFAULT_TAG}]"
read TAG

# set default
if [ "$TAG" = "" ]; then
    TAG=$DEFAULT_TAG
fi

# merge develop
git checkout master
git pull origin master
git merge develop
git push origin master

# delete old tag
if [ "$(git tag | grep $TAG)" != "" ]; then
    git tag -d $TAG
    git push origin :refs/tags/$TAG
fi

# create new tag
git tag -a $TAG -m "$TAG"
git push origin $TAG

# back to develop branch
git checkout develop
echo "Release done."
