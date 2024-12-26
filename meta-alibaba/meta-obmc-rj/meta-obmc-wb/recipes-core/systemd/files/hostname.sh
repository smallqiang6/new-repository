#!/bin/bash
HOSTNAME="bmc"

set_hostname() {
  local name=$1
  # Update /etc configuration and persistent cache.
  echo "$name" > /etc/hostname
  echo "$name" > /mnt/data/hostname
  # Set hostname
  hostname "$name"
}

arg_hostname=$1
if [ ! -z $arg_hostname ]; then
  HOSTNAME=$arg_hostname
else
  if [ -s /mnt/data/hostname ]; then
    # Use the cached copy to set the hostname
    HOSTNAME="$(cat /mnt/data/hostname)"
  fi
fi
set_hostname "$HOSTNAME"
logger -t hostname.sh -p user.info "config hostname: $HOSTNAME done."