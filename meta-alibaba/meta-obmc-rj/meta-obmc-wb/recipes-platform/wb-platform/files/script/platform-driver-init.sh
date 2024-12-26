#!/bin/bash

findmtd() {
	m=$(grep -xl "$1" /sys/class/mtd/*/name)
	m=${m%/name}
	m=${m##*/}
	echo $m
}

get_fw_env_var() {
	# do we have 1 or 2 copies of the environment?
	# count non-blank non-comment lines
	# copies=$(grep -v ^# /etc/fw_env.config | grep -c [::alnum::])
	# ... we could if we had the fw_env.config in the initramfs
	copies=1

	# * Change \n to \r and \0 to \n
	# * Skip to the 5th byte to skip over crc
	# * then skip to the first or 2nd byte to skip over flag if it exists
	# * stop parsing at first empty line corresponding to the
	#   double \0 at the end of the environment.
	# * print the value of the variable name passed as argument

	envdev=$(findmtd env)
	if test -n $envdev
	then
		head -c 1000 /dev/$envdev |
		tr '\n\000' '\r\n' |
		tail -c +5 | tail -c +${copies-1} |
		sed -ne '/^$/d' -e "s/^$1=//p"
	fi
}

# Gets productname in the environment variable
PRODUCTNAME_ENV=$(get_fw_env_var productname)
PRODUCTNAME=${PRODUCTNAME_ENV##*=}

BOARD_ENV=$(get_fw_env_var board_id)
BOARD_ID=${BOARD_ENV##*=}
ID="0x"$(printf %x $BOARD_ID)

bsp_cmd="/usr/local/bin/$PRODUCTNAME-$ID-platform.sh"
echo "running platform driver init $bsp_cmd"
eval $bsp_cmd
exit 0
