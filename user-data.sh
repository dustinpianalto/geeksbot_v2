#!/bin/bash

yum update -y
export AWS_DEFAULT_REGION='us-east-1'
instance_id=$(wget -q -O - http://169.254.169.254/latest/meta-data/instance-id)
aws ec2 associate-address --instance-id $instance_id --public-ip "34.238.62.161"
mkdir /code || exit
cd /code || exit
git clone git@github.com:dustinpianalto/geeksbot_v2.git
cd geeksbot_v2 || exit
docker build . -t geeksbot || exit
docker run -d -v /code/geeksbot_v2:/code -v /root/.ssh:/root/.ssh:ro --name geeksbot --restart always geeksbot:latest || exit
