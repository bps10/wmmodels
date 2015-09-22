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
	local shape=full_field
    else 
	local shape=$3
    fi

    # print out what we are doing
    echo ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -shape $shape -t $H2P0 \
	noblock $analysis $secondopt

    # now run the model
    ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -shape $shape -t $H2P0 \
	noblock $analysis $secondopt
}

function move_files {
    mv results/img/macaque/s_dist_hist.svg \
	results/img/macaque/$1/$2/s_dist_hist.svg
    mv results/img/macaque/s_dist_scatter.svg \
	results/img/macaque/$1/$2/s_dist_scatter.svg
    # move into s_dist folder to globstar move nd files
    cd results/nd_files/macaque/s_dist/
    mv *.nd ../../../../results/img/macaque/$1/$2/
    cd ../../../../
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

### coneiso plots
function cone_input_plots {
    # change param to random
    RAN_S=true 
    DIR=random
    run_model cone_inputs
    cd results/img/macaque/
    mkdir -p $DIR/cone_inputs/
    mv cone_inputs* $DIR/cone_inputs/
    cd ../../../

    # change param to non random
    RAN_S=false
    DIR=nonrandom
    run_model cone_inputs
    cd results/img/macaque/
    mkdir -p $DIR/cone_inputs/
    mv cone_inputs*.svg $DIR/cone_inputs/
    cd ../../../
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
	
# create directory to save everything
	mkdir -p results/img/macaque/$DIR/
	mkdir -p results/img/macaque/$DIR/uniform/
	mkdir -p results/img/macaque/$DIR/5cpd/
	mkdir -p results/img/macaque/$DIR/spot/

# save mosaic files
	run_model mosaic
	mv results/img/mosaic/mosaic.svg results/img/macaque/$DIR/mosaic.svg

# Uniform (full field)
	run_model s_dist foo full_field
	move_files $DIR full_field

# 5 cpd grating
	run_model s_dist foo grating
	move_files $DIR 5cpd

# Small spot
## also need to change cone here for the random case, otherwise not centered
	run_model s_dist foo spot
	move_files $DIR spot

done
}


function verbose_plots {

    # generate models and plots
    space_time_plots

    step_function 

    cone_iso_plots

    sf_tuning_plots

    #tf_tuning_plots

    s_dist_plots
    
    cone_input_plots

}


function main {
    # check if eccentricity passed as input arg
    if [ "$#" -gt 0 ];
    then 
	eccentricity=$1;
    else
	eccentricity=fovea;
    fi
    if [ "$#" -gt 1 ];
    then
	H2P0=$2
    else
	H2P0=0.0
    fi
    echo Eccentricity set to: $eccentricity
    echo H2 percept0 set to: $H2P0

    # Params 
    #                    H1GP, H1GH, H1W,  H2GP, H2GH, H2W 
    # eccentric loc =   (0.15, 2.0,  0.7,  1.0,  1.0,  0.4)
    # fovea (WT-like) = (0.15, 0.04, 0.65, 1.3,  0.02, 0.4)
    if [ "$eccentricity" == "fovea" ]
    then
	H1GP=0.15
	H1GH=0.04
	H1W=0.65
	H2GP=1.3
	H2GH=0.02
	H2W=0.4
	RAN_S=false
    elif [ "$eccentricity" == "periph" ] || [ "$eccentricity" == "periphery" ]
    then
	H1GP=0.15
	H1GH=2.0
	H1W=0.65
	H2GP=1.0
	H2GH=1.0
	H2W=0.4
	RAN_S=false
    else
	echo $1 not understood. Eccentricity must be fovea or periphery
    fi
    ### save parameters to directory
    ./retina.sh params -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -t $H2P0 > \
	results/img/macaque/start_params

    verbose_plots
}

# run main function
main $1 $2