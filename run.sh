#!/bin/bash

##########################################################
# Setting default variables
logtimestamp=$(date +"%Y-%m-%d_%H-%M-%S")

##########################################################
# Setting variables

export SHELL_SCRIPT_NAME='run'
export SHELL_SCRIPT_FOLDER=$(pwd)
export LOGDIR=${SHELL_SCRIPT_FOLDER}/log
export LOG_FILE=${LOGDIR}/${SHELL_SCRIPT_NAME}_${logtimestamp}.log

##########################################################
# Changing directory
cd ${SHELL_SCRIPT_FOLDER}

##########################################################
# Setting log rules
exec > >(tee ${LOG_FILE}) 2>${LOGDIR}/error.log

##########################################################
# Running python script
source sandbox/bin/activate

echo "Starting Python Execution"
python3 ${SHELL_SCRIPT_FOLDER}/run.py

# Checking Python errors
RC1=$?
if [ ${RC1} != 0 ]; then
	echo "PYTHON RUNNING FAILED"
	echo "[ERROR:] RETURN CODE:  ${RC1}"
	echo "[ERROR:] REFER TO THE ERROR LOG FOR THE REASON FOR THE FAILURE."
	exit 1
fi

echo "SH SCRIPT RAN SUCCESSFULLY"

exit 0