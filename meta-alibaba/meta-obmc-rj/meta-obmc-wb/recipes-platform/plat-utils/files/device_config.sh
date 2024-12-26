#!/bin/bash

mkdir -p /home/root/.ssh
cp  /etc/id_rsa.pub /home/root/.ssh/authorized_keys
chmod 700 /home/root/.ssh
chmod 644 /home/root/.ssh/authorized_keys

