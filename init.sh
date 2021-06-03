#!/bin/bash

export "PATH=$PATH:/snap/bin"
docker stop sluchakbot || true
docker rmi sluchakbot_image || true
docker build -t sluchakbot_image .
docker run -d --rm --network="host" --name sluchakbot -v "$(pwd)/var":/var sluchakbot_image