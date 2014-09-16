#!/bin/bash

# H1 and H2 gp options
MODEL=${1:-human} # Set the model to use
H1GP=${2:-0.1} # Set H1 cell gp. Default = 0.1
H2GP=${3:-0.6} # Set H2 cell gp. Default = 0.6
H2GH=${4:-1.8} # Set H2 cell gh. Default = 1.8

# Analysis options
OPTS=${5:-h1} # Set H2 cell gp. Default =0.6

echo "h1 gp is set to: $H1GP"
echo "h2 gp is set to: $H2GP"
echo "h2 gh is set to: $H2GH"
echo "model is set to: $MODEL"
echo "analysis option: $OPTS"
echo " "

if [[ $OPTS == "h1" || $OPTS == "verbose" ]]
	then
		if [ -e "results/pl_files/h1.dist.pl" ] 
			then
				rm results/pl_files/h1.dist.pl
				echo "rm results/pl_files/rm h1.dist.pl"
		fi	
		wm mod ${MODEL}/Ret_Mesh_H2.moo stim/test_gray.stm ${MODEL}/retina.rsp  tn 512 \
		retina0/h_mesh.h1/gp ${H1GP} \
		retina0/h_mesh.h2/gp ${H2GP} \
		retina0/h_mesh.h2/gh ${H2GH} \
		retina0/stim_override 1 \
		retina0/mesh_dump_type h_v_dist

		if [ $OPTS != "verbose" ]
			then
				python results ${OPTS} ${MODEL}
		fi

fi

if [[ $OPTS == "h2" || $OPTS == "verbose" ]]
	then
		if [ -e "results/pl_files/h2.dist.pl" ] 
			then
				rm results/pl_files/h2.dist.pl
				echo "rm results/pl_files/rm h2.dist.pl"
		fi	
		# Everything is reversed here!
		wm mod ${MODEL}/Ret_Mesh_H2_H1_reverse.moo stim/test_gray.stm ${MODEL}/retina.rsp  tn 512 \
		retina0/h_mesh.h2/gp ${H1GP} \
		retina0/h_mesh.h1/gp ${H2GP} \
		retina0/h_mesh.h1/gh ${H2GH} \
		retina0/stim_override 1 \
		retina0/mesh_dump_type h_v_dist

		python results ${OPTS} ${MODEL}
fi

if [[ $OPTS == "h1_spat" || $OPTS == "verbose" ]]
	then
		if [ -e "results/nd_files/zz.nd" ]
			then
				rm zz.nd
		fi
		wm mod ${MODEL}/Ret_Mesh_H2.moo stim/test_gray.stm ${MODEL}/retina.rsp  tn 512 \
			retina0/h_mesh.h1/gp ${H1GP} \
			retina0/h_mesh.h2/gp ${H2GP} \
			retina0/h_mesh.h2/gh ${H2GH} \
			retina0/stim_override 1 \
			retina0/stim_override_binary all

		java -jar ~/Projects/wmbuild/nd.jar results/nd_files/zz.nd
fi


echo "end script"
echo "--------------"
echo " "