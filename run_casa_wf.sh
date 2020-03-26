#!/usr/bin/env bash

dax_name=$(python daxgen.py -o dax_outputs -f /nfs/shared/ldm/FORCING.tar.gz -c /home/ldm/wrfworkflow/input/wrf_config.tar)
echo $dax_name;
./plan.sh ${dax_name}


