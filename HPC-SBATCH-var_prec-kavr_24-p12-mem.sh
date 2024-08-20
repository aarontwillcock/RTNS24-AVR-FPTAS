#!/bin/bash
# Job name
#SBATCH --job-name vp-k-p12-m
# Submit to the primary QoS
#SBATCH -q primary
# Request one node
#SBATCH -N 1
# Total number of cores, in this example it will 1 node with 1 core each. 
#SBATCH -n 1
# Request memory
#SBATCH --mem=1024GB
# Mail when the job begins, ends, fails, requeues 
#SBATCH --mail-type=ALL
# Where to send email alerts
#SBATCH --mail-user=ez9213@wayne.edu
# Create an output file that will be output_<jobid>.out 
#SBATCH -o output_%j.out
# Create an error file that will be error_<jobid>.out
#SBATCH -e errors_%j.err
# Set maximum time limit
#SBATCH -t 2-0:0:0
# Set pref to MEM cluster
#SBATCH -w mem[1-9]

#Variable Precision - KAVR18 included
python3 var_prec-kavr_24-p12-mem.py