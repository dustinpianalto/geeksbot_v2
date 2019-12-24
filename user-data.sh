#!/bin/bash

yum update -y
mkdir /code || exit
cd /code || exit
git clone git@github.com:dustinpianalto/geeksbot_v2.git
cd geeksbot_v2 || exit
docker build . -t geeksbot || exit
docker run -d -v /code/geeksbot_v2/geeksbot:/code/geeksbot --name geeksbot --restart always geeksbot:latest || exit