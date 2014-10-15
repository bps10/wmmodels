#!/bin/bash

# Import utility fuctions
. $PWD/retina_util.sh

#-- 0. Set default parameters
H1GP=0.1
H2GP=0.6
H2GH=1.8
H2S=0.7
H2M=0.15
H2L=0.15
H2W=0.2
TN=512

# setup conditions to specify behavior
analysis=(siso coneiso h1 h2 h_time mosaic gui stack nd plot \
    verbose)
runmod=(h1 h2 siso coneiso h_time)
plots=(h1 h2 siso coneiso stack h_time verbose)
dump=(siso coneiso h_time)

#-- 1. Get analysis option
MODEL=macaque
OPTS=()
args=("$@")
i=0
while [ $i -lt $# ]; do

    if [[ ${args[$i]} == human ]]
    then
	MODEL=human
    fi

    if [ $(exists_in ${args[$i]} "${analysis[*]}") == true ]
    then
	OPTS+=(${args[$i]})
    fi
    
    H1GP=$(check_arg -P $H1GP)
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

#-- 4. Delete old output files
if [ -e "results/pl_files/$OUT_FILE" ] 
then
    rm results/pl_files/${OUT_FILE}
    echo "rm results/pl_files/rm $OUT_FILE"
fi	

#-- 5. Perform the simulation(s)
if [ $OPTS == "mosaic" ]
then
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
	response/retina.rsp  tN ${TN}  gui_flag 1 \
	retina0/mesh_dump_type mosaic_coord \
	retina0/mesh_dump_file zz.mosaic
    
    python results mosaic

elif [ $OPTS == "gui" ]
then
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
	response/retina.rsp  tn ${TN}  \
	gui_flag 1
else


    if [ $(exists_in ${OPTS} "${runmod[*]}") == true ]
    then
	run_wm ${MODEL} ${MOO_FILE} ${STIM_FILE}

        #-- dump results when necessary
	if [ $(exists_in ${OPTS} "${dump[*]}") == true ]
	then
	    ~/Projects/wmbuild/bin/ndutil nd2text \
		results/nd_files/zz.nd \
		results/txt_files/zz.txt 
	fi
    fi

fi

#-- 6. Plotting routines
if [ $(exists_in ${OPTS[0]} "${plots[*]}") == true ]
then
    python results ${OPTS} ${MODEL}
elif [ $(exists_in ${OPTS[1]} "${plots[*]}") == true ]
then
    python results ${OPTS[1]} ${MODEL}
fi

#-- 7. Start nd viewer when appropriate
if [[ $OPTS == "nd" ]]
then
    java -jar ~/Projects/wmbuild/bin/nd.jar results/nd_files/zz.nd
fi

echo " "
echo "end script"
echo "--------------"
echo " "