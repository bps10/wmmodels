#!/bin/bash

# Import utility fuctions
. ./util/retina_util.sh

# Import default parameters
. ./util/default_vars.sh

#-- 1. Import model specific parameters

# find if model has been changed
args=("$@")
i=0
while [ $i -lt $# ]; do
    MODEL=$(check_arg -model $MODEL)
    i=$((i+1))
done

# load appropriate model vars
. ./models/${MODEL}/default_vars.sh

#-- 2. Get analysis option

# setup conditions to specify behavior
analysis=(siso miso liso coneiso h1 h2 \
    h_time mosaic gui stack nd plot \
    verbose params knn h_sf bp_sf rgc_sf \
    h_tf bp_tf rgc_tf \
    s_dist cone_inputs step)
runmod=(h1 h2 siso miso liso coneiso h_time knn h_sf bp_sf rgc_sf \
    h_tf bp_tf rgc_tf \
    cone_inputs gui step)
plots=(h1 h2 siso miso liso coneiso stack h_time verbose knn h_sf \
    bp_sf rgc_sf h_tf bp_tf rgc_tf s_dist cone_inputs step)
dump=(siso miso liso coneiso h_time knn h_sf bp_sf rgc_sf \
    h_tf bp_tf rgc_tf cone_inputs step)
iso_cond=(siso miso liso coneiso)

OPTS=()
i=0
while [ $i -lt $# ]; do

    if [ $(exists_in ${args[$i]} "${analysis[*]}") == true ]
    then
	OPTS+=(${args[$i]})
    fi

    FUND=$(check_arg -fund $FUND)
    SHAPE=$(check_arg -shape $SHAPE)
    RANDOM_S=$(check_arg -ran_s $RANDOM_S)
    H1GP=$(check_arg -P $H1GP)
    H1GH=$(check_arg -H $H1GH)
    H1P0=$(check_arg -T $H1P0)
    H1ES=$(check_arg -E $H1ES)
    H1W=$(check_arg -W $H1W)
    H2GP=$(check_arg -p $H2GP) 
    H2GH=$(check_arg -h $H2GH)
    H2P0=$(check_arg -t $H2P0)
    H2ES=$(check_arg -e $H2ES)
    H2S=$(check_arg -s $H2S)
    H2M=$(check_arg -m $H2M)
    H2L=$(check_arg -l $H2L)
    H2W=$(check_arg -w $H2W)
    TN=$(check_arg -tn $TN)

    i=$((i+1))
done
check_gui_flag

check_block_plots_flag

#-- 3. Print some info about parameters or a help file
print_info

#-- 4. Change the model behavior based on command line input
change_parameters

#-- 5. Change system matrix
change_sys_matrix

#-- 6. Delete old output files
delete_old_file

#-- 7. Perform the simulation(s)
if [ $OPTS == "mosaic" ]
then
    run_mosaic

elif [ $OPTS == "s_dist" ]
then
    run_s_dist_analysis

else

    if [ $(exists_in ${OPTS} "${runmod[*]}") == true ]
    then
	run_wm ${MODEL} ${STIM_FILE}
	
	if [ $GUI == 0 ] # make sure model was truly run
	then
	#-- save current variables as new defaults
	    save_defaults
	fi
    fi

fi

#-- 8. Plotting routines
if [[ $(exists_in ${OPTS[0]} "${plots[*]}") == true && $GUI == 0 ]]
then
    python pycomp ${MOSAIC_FILE} ${OPTS} ${MODEL} ${SHAPE} ${BLOCK_PLOTS}
elif [[ $(exists_in ${OPTS[1]} "${plots[*]}") == true  && $GUI == 0 ]]
then
    python pycomp ${MOSAIC_FILE} ${OPTS[1]} ${MODEL} ${SHAPE} ${BLOCK_PLOTS}
fi

#-- 9. Start nd viewer when appropriate
if [[ $OPTS == "nd" ]]
then
    java -jar ~/Projects/wmbuild/bin/nd.jar results/nd_files/zz.nd
fi

echo " "
echo "end script"
echo "--------------"
echo " "