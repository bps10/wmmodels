#!/bin/bash

# ------- Parameters ------- #
# Model (subject) to use for analysis
MODEL=WT
# add "plot" here if you only want to read in
PLOT_OPT=plot
# get formatted date for save name
DATE=`date +%Y-%m-%d`
# results save name
FILENAME=$(file_name results/img/classification/${MODEL}/classify_results \
    .txt $DATE)

# -------------- subfunctions ------------- #
function file_name {
    local fname=$1
    local extension=$2
    local date=$3
    local keepgoing=1
    local numID=1
    while [ $keepgoing == 1 ]; do
	testname="${fname}_${date}_${numID}${extension}"
	if [ ! -f $testname ]; then
	    numID=$(($numID+1))
	    keepgoing=0
	else
	    keepgoing=0
	fi
    done
    echo $testname
}
# ----------------------------------------- #

function main {
# Run the simulations 
    echo "Simulation 1"
    ./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.4 -W 0.65 \
	-ran_cone false noblock > $FILENAME
    
    echo "Simulation 2"
    ./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.0 -W 1.0 \
	-ran_cone false noblock >> $FILENAME
    
#### Add a randomized mosaic control for comparison
    echo "Simulation 3"
    ./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.4 -W 0.65 \
	-ran_cone true noblock >> $FILENAME
    
    echo "Simulation 4"
    ./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.0 -W 1.0 \
	-ran_cone true noblock >> $FILENAME
}

# run the main function
main