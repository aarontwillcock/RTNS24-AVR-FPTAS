#!/bin/bash
# Job name
#SBATCH --job-name KAVR_cProfile
# Submit to the primary QoS
#SBATCH -q primary
# Request one node
#SBATCH -N 1
# Total number of cores, in this example it will 1 node with 1 core each. 
#SBATCH -n 1
# Request memory
#SBATCH --mem=128G
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
# Set pref to MDT cluster
#SBATCH -w mdt[1-83]

python3 -m cProfile -s calls var_dur-kavr18-why-slow-10s.py > var_dur-kavr18-10s-calls.cProfile
python3 -m cProfile -s calls var_dur-kavr18-why-slow-20s.py > var_dur-kavr18-20s-calls.cProfile