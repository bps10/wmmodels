#!/bin/bash

#---- sub routines ----#
function run_model {
    local analysis=$1
    if [ "$2" == "foo" ]
    then
	local secondopt=
    else
	local secondopt=$2 # often doesn't exist
    fi
    if [ -z $3 ]
    then 
	local shape=uniform
    else 
	local shape=$3
    fi

    # print out what we are doing
    echo ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -shape $shape \
	noblock $analysis $secondopt

    # now run the model
    ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -shape $shape \
	noblock $analysis $secondopt
}
# -------------------- #

function space_time_plots {

    run_model h1
    run_model h2
    run_model h_time
    run_model plot verbose

}

### step function
function step_function {
    
    run_model step

}

### coneiso plots
function cone_iso_plots {
    run_model coneiso
}

### sf tuning plots
function sf_tuning_plots {

    run_model h_sf
    run_model plot bp_sf
    run_model plot rgc_sf
}

### tf tuning plots
function tf_tuning_plots {

    run_model h_tf    
    run_model plot bp_tf
    run_model plot rgc_tf
}

### s_dist plots
function s_dist_plots {

    for i in `seq 1 2`; do
	
	if [ $i -eq 1 ]
	then
	    RAN_S=true # change param to random
	    DIR=random
	else
	    RAN_S=false
	    DIR=nonrandom
	fi

# save mosaic files
	run_model mosaic
	
# Uniform
	run_model s_dist foo uniform

# 5 cpd grating
	run_model s_dist foo grating

# Small spot
## also need to change cone here for the random case, otherwise not centered
	run_model s_dist foo spot

done
}


function verbose_plots {

    # generate models and plots
    space_time_plots

    step_function 

    cone_iso_plots

    sf_tuning_plots

    tf_tuning_plots

    s_dist_plots
}


function main {

    # Params
    H1GP=0.15
    H1GH=2.0
    H1W=0.7
    H2GP=1.0
    H2GH=1.0
    H2W=0.4
    RAN_S=false

    ### save parameters to directory
    echo ./retina.sh params > results/macaque/start_params

    verbose_plots
}

# run main function
main