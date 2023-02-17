#!/usr/bin/env bash

if [ $# -ne 3 ]; then
  echo 1>&2 "Usage: $0 IMAGE-NAME COMPONENT-NAME COMPONENT-VERSION"
  exit 3
fi

IMAGE_NAME=$1
COMPONENT_NAME=$2
VERSION=$3

mkdir -p ./greengrass-build/artifacts/$COMPONENT_NAME/$VERSION

mkdir -p ./greengrass-build/recipes/
cp recipe.yaml ./greengrass-build/recipes/

docker build -t $IMAGE_NAME:$VERSION src/
docker save --output ./greengrass-build/artifacts/$COMPONENT_NAME/$VERSION/image.tar.gz $IMAGE_NAME:$VERSION
