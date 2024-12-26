#!/bin/bash
# Copyright (C) 2023, Ruijie Networks Co., Ltd. All rights reserved.
# No part of this script may be reproduced, distributed,
# or transmitted in any form or by any means,
# without the prior written permission of the author.
bmc_path=$(pwd)
ali_bmc_path="/meta-alibaba/meta-obmc-rj/"
ali_bmc_version="recipes-utils/rj-util/files/bmc_module_version"
ali_module="openbmc"
rj_module="openbmc-platform-ruijie"
ali_commit=$(git rev-parse --short HEAD)
ali_branch=$(git rev-parse --abbrev-ref HEAD)
cd $bmc_path$ali_bmc_path
rj_commit=$(git rev-parse --short HEAD)
rj_branch=$(git rev-parse --abbrev-ref HEAD)
cd $bmc_path
echo "$ali_module $ali_branch $ali_commit"   > version
echo "$rj_module $rj_branch $rj_commit"  >> version
gawk 'BEGIN{print "MODULE BRANCH  COMMIT_ID"};{print $1" "$2" "$3}' version | column -t > $bmc_path$ali_bmc_path$ali_bmc_version
rm version

