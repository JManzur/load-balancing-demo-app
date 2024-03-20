#!/bin/bash

set -e

IMAGE="jmanzur/demo-lb-app:latest"
PORT="8882"

image_build() {
  echo "Building image: $IMAGE"
  docker build -t $IMAGE .
  docker-compose up -d
}

echo "Stopping and removing container: $IMAGE"
echo ""
docker-compose down
if docker images | awk '{print $1 ":" $2}' | grep -q "$IMAGE"; then
    docker rmi "$IMAGE"
    if [ $? -eq 0 ]; then
        echo "Image removed successfully."
        image_build
    else
        echo "Failed to remove the image."
    fi
else
    echo "The image '$IMAGE' does not exist."
    image_build
fi

# Check the exit status of the previous command
if [ $? -eq 0 ]; then
  echo ""
  echo "Application URL: http://localhost:$PORT"
  echo ""
  exit 0
else
  echo ""
  echo "Error: The process was not successful"
  echo ""
  exit 1
fi