#!/bin/bash

docker build -t static-checker:latest .
docker run -it static-checker:latest
