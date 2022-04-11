#!/usr/bin/env bash

# Prerequisites:
#   * git, jq, aws cli
#
#   git clone https://github.com/aws-samples/aws-iot-securetunneling-localproxy.git
#   cd aws-iot-securetunneling-localproxy
#   ./docker-build.sh

if [[ -z "$1" ]] ; then
    echo "Error: thing name missing."
    exit 1
fi

export AWS_REGION=$(aws configure get region)
export AWS_PAGER=""
r=$(aws iotsecuretunneling open-tunnel --destination-config=thingName="${1}",services=SSH)
tunnelId=$(echo ${r} | jq -r '.tunnelId')
sourceAccessToken=$(echo ${r} | jq -r '.sourceAccessToken')

echo "Secure Tunnel created with tunnelId: ${tunnelId}."

function cleanup() {
    aws iotsecuretunneling close-tunnel --tunnel-id ${tunnelId}
    echo "Secure Tunnel ${tunneId} closed."
}
trap cleanup EXIT

docker run \
    --name localproxy \
    --rm \
    -it \
    -p 2222:22 \
    -e AWSIOT_TUNNEL_ACCESS_TOKEN="${sourceAccessToken}" \
    aws-iot-securetunneling-localproxy:latest \
    ./localproxy -r ${AWS_REGION} -b 0.0.0.0 -s 22
