#!/bin/bash

# H1 and H2 gp options
H1GP=${1:-0.1} # Set H1 cell gp. Default = 0.1
H2GP=${2:-0.6} # Set H2 cell gp. Default = 0.6
H2GH=${3:-1.8} # Set H2 cell gh. Default = 1.8

# Analysis options
OPTS=${4:-h1_rf} # Set H2 cell gp. Default =0.6

echo "h1 gp is set to: $H1GP"
echo "h2 gp is set to: $H2GP"
echo "h2 gh is set to: $H2GH"
echo "analysis option: $OPTS"

if [[ $OPTS == "h1_rf" || $OPTS == "verbose" ]]
	then
		if [ -e "h1.dist.pl" ] 
			then
				rm h1.dist.pl
				echo "rm h1.dist.pl"
		fi	
		wm mod ret4/Ret_Mesh_H2.moo stim/test_gray.stm ret4/retina.rsp  tn 512 \
		retina0/h_mesh.h1/gp ${H1GP} \
		retina0/h_mesh.h2/gp ${H2GP} \
		retina0/h_mesh.h2/gh ${H2GH} \
		retina0/stim_override 1 \
		retina0/mesh_dump_type h_v_dist

		if [ $OPTS -ne "verbose" ]
			then
				python results/plot_dist.py
		fi

fi

if [[ $OPTS == "h2_rf" || $OPTS == "verbose" ]]
	then
		if [ -e "h2.dist.pl" ] 
			then
				rm h2.dist.pl
		fi	
		# Everything is reversed here!
		wm mod ret4/Ret_Mesh_H2_H1_reverse.moo stim/test_gray.stm ret4/retina.rsp  tn 512 \
		retina0/h_mesh.h2/gp ${H1GP} \
		retina0/h_mesh.h1/gp ${H2GP} \
		retina0/h_mesh.h1/gh ${H2GH} \
		retina0/stim_override 1 \
		retina0/mesh_dump_type h_v_dist

		python results/plot_dist.py
fi

if [[ $OPTS == "h1_spat" || $OPTS == "verbose" ]]
	then
		if [ -e "zz.nd" ]
			then
				rm zz.nd
		fi
		wm mod ret4/Ret_Mesh_H2.moo stim/test_gray.stm ret4/retina.rsp  tn 512 \
			retina0/h_mesh.h1/gp ${H1GP} \
			retina0/h_mesh.h2/gp ${H2GP} \
			retina0/h_mesh.h2/gh ${H2GH} \
			retina0/stim_override 1 \
			retina0/stim_override_binary all

		java -jar ~/Projects/wmbuild/nd.jar zz.nd
fi


echo "end script"
echo "--------------"
echo " "