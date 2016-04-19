#!/bin/bash

# Model (subject) to use for analysis
MODEL=WT
# add "plot" here if you only want to read in
PLOT_OPT=plot
# get formatted date for save name
DATE=`date +%Y-%m-%d`

# 
echo "Simulation 1"
./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.4 -W 0.65 \
    -ran_cone false noblock > \
    results/img/${MODEL}/classify_results_${DATE}.txt

echo "Simulation 2"
./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.0 -W 1.0 \
    -ran_cone false noblock >> \
    results/img/${MODEL}/classify_results_${DATE}.txt

#### Add a randomized mosaic control for comparison
echo "Simulation 3"
./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.4 -W 0.65 \
    -ran_cone true noblock >> \
    results/img/${MODEL}/classify_results_${DATE}.txt

echo "Simulation 4"
./retina.sh -model $MODEL $PLOT_OPT iso_classify -w 0.0 -W 1.0 \
    -ran_cone true noblock >> \
    results/img/${MODEL}/classify_results_${DATE}.txt