#!/bin/bash

# Import utility fuctions
. ./util/retina_util.sh

# Import default parameters
. ./util/default_vars.sh

# setup conditions to specify behavior
analysis=(siso coneiso h1 h2 miso liso \
    h_time mosaic gui stack nd plot \
    verbose params knn h_sf)
runmod=(h1 h2 siso miso liso coneiso h_time knn h_sf)
plots=(h1 h2 siso miso liso coneiso stack h_time verbose knn h_sf)
dump=(siso miso liso coneiso h_time knn h_sf)
iso_cond=(siso miso liso coneiso)

#-- 1. Get analysis option
OPTS=()
args=("$@")
i=0
while [ $i -lt $# ]; do

    if [ $(exists_in ${args[$i]} "${analysis[*]}") == true ]
    then
	OPTS+=(${args[$i]})
    fi
    
    MODEL=$(check_arg -model $MODEL)
    FUND=$(check_arg -fund $FUND)
    SHAPE=$(check_arg -shape $SHAPE)
    H1GP=$(check_arg -P $H1GP)
    H1GH=$(check_arg -H $H1GH)
    H2GP=$(check_arg -p $H2GP) 
    H2GH=$(check_arg -h $H2GH)
    H2S=$(check_arg -s $H2S)
    H2M=$(check_arg -m $H2M)
    H2L=$(check_arg -l $H2L)
    H2W=$(check_arg -w $H2W)
    TN=$(check_arg -t $TN)

    i=$((i+1))
done

#-- 2. Print some info about parameters or a help file
print_info

#-- 3. Change the model behavior based on command line input
change_parameters

#-- 4. Change system matrix
change_sys_matrix

#-- 5. Delete old output files
delete_old_file

#-- 6. Perform the simulation(s)
if [ $OPTS == "mosaic" ]
then
    run_mosaic

elif [ $OPTS == "gui" ]
then
    run_gui

else

    if [ $(exists_in ${OPTS} "${runmod[*]}") == true ]
    then
	run_wm ${MODEL} ${STIM_FILE}
	
	#-- save current variables as new defaults
	save_defaults

        #-- dump results when necessary
	dump_results
    fi

fi

#-- 7. Plotting routines
if [ $(exists_in ${OPTS[0]} "${plots[*]}") == true ]
then
    python pycomp ${OPTS} ${MODEL}
elif [ $(exists_in ${OPTS[1]} "${plots[*]}") == true ]
then
    python pycomp ${OPTS[1]} ${MODEL}
fi

#-- 8. Start nd viewer when appropriate
if [[ $OPTS == "nd" ]]
then
    java -jar ~/Projects/wmbuild/bin/nd.jar results/nd_files/zz.nd
fi

echo " "
echo "end script"
echo "--------------"
echo " "