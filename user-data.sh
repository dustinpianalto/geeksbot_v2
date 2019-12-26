#!/bin/bash

export AWS_DEFAULT_REGION='us-east-1'
instance_id=$(wget -q -O - http://169.254.169.254/latest/meta-data/instance-id)

role=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$instance_id" | grep -2 role | grep Value | tr -d ' ' | cut -f2 -d: | tr -d '"' | tr -d ',')
if [ "$role" = "development" ]; then
  aws ec2 associate-address --instance-id "$instance_id" --public-ip "3.211.100.13"
  git checkout development
else
  aws ec2 associate-address --instance-id "$instance_id" --public-ip "34.238.62.161"
  git checkout master
fi
docker build . -t geeksbot || exit
docker run -d -v /code/geeksbot_v2:/code -v /root/.ssh:/root/.ssh:ro --name geeksbot --restart always geeksbot:latest || exit
