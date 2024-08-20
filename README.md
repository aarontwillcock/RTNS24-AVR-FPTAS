# A Fully Polynomial Time Approximation Scheme for Adaptive Variable Rate Task Demand

This repo contains anonymized source code for the RTNS'24 paper:
"A Fully Polynomial Time Approximation Scheme for Adaptive Variable Rate Task Demand"

## Acknowledgments

<table width="100%" style="text-align: center" cellpadding="20">
  <tr>
    <td style="vertical-align:middle">
        <a href="https://www.nsf.gov">
            <img src="https://www.nsf.gov/news/mmg/media/images/nsf%20logo_ba604992-ed6d-46a7-8f5b-151b1c3e17e3.jpg" alt="NSF" height="100px"/>
        </a>
    </td>
    <td style="vertical-align:middle">
        <a href="https://vt.edu">
            <img src="https://www.assets.cms.vt.edu/images/HorizontalStacked/HorizontalStacked_RGB.svg" height="63px"/>
        </a>
    </td>
    <td style="vertical-align:middle">
        <a href="https://wayne.edu">
            <img src="https://mac.wayne.edu/images/wsu_primary_horz_color.png" height="50px"/>
        </a>
    </td>
  </tr>
</table>

This research has been supported in part by the [US National Science  Foundation](https://www.nsf.gov/).

## Authors - Contact

| Author | Department | University | Location | Email |
| ------ | ---------- | ---------- | -------- | ----- |
| [Thidapat Chantem](https://ece.vt.edu/people/profile/chantem) | Electrical and Computer Engineering | [Virginia Tech](https://vt.edu/index.html) | Arlington, VA, USA | tchantem@vt.edu |
| [Nathan Fisher](https://engineering.wayne.edu/profile/dx3281) | Computer Science | [Wayne State University](https://wayne.edu/) | Detroit, MI, USA | fishern@wayne.edu |
| [Aaron Willcock](https://www.linkedin.com/in/aaronwillcock/) | Computer Science | [Wayne State University](https://wayne.edu/) | Detroit, MI, USA | willcock@wayne.edu |

## Table of Contents
- [A Fully Polynomial Time Approximation Scheme for Adaptive Variable Rate Task Demand](#a-fully-polynomial-time-approximation-scheme-for-adaptive-variable-rate-task-demand)
  - [Acknowledgments](#acknowledgments)
  - [Authors - Contact](#authors---contact)
  - [Table of Contents](#table-of-contents)
  - [Predefined Sequence Bounded Precedence Constraint Knapsack Problem Experiment Run Instructions](#predefined-sequence-bounded-precedence-constraint-knapsack-problem-experiment-run-instructions)
  - [Source Code Structure](#source-code-structure)
  - [Brief Summary](#brief-summary)

## Predefined Sequence Bounded Precedence Constraint Knapsack Problem Experiment Run Instructions

1. Identify an experiment from the src/* folder level (e.g., var_prec-kavr_24-p05.py) you wish to run
2. Execute python3 var_prec-kavr_24-p05.py
3. Allow simulation to finish
4. Review results in exp_data folder

## Source Code Structure

1. Literature implementations can be found in bpckp_fxns/*
   1. KAVR = KAVR_24.py
   2. EXACT = bpckp_fptas.py:calculate_demand_seq() with apx = 0
   2. APX = bpckp_fptas.py:calculate_demand_seq() with apx = 1
2. Mohaqeqi et al. "Refinement of Workload..." from ECRTS'17 is also implemented as ROW_17.py

## Brief Summary
1.  apx_fxns/ - Contains classes, functions required for APX execution
2.  avr_fxns/ - Defines AVR tasks and tools to generate AVR tasks
3.  bpckp_fxns/ - Defines demand calculation algorithms
4.  csv_fxns/ - Tools for exporting to CSV
5.  exp_data/ - Location for experimental data to be placed, source of GNUPLOT data for creating figures
    1.  exp_data/pub_data/ - Raw data used to create aggregate data files with timestamps
6.  outpit_file_name_gen/ - Tool for create filenames based on experiment
7.  sxs_fxns/ - Functions for running experiments with different demand calculation algorithms
8.  task_sets/ - Classes of task sets from literature, from random generations, and for validation testing
9.  HPC-BASH-* - Scripts to run on a SLURM-capable HPC grid (requires modification for node names)
10. HPC-SBATCH-* - Scripts to call with SBATCH on a SLURM-capable HPC grid (requires modification for node names)
11. var_XXX-* - An experiment for testing variable XXX versus runtime where XXX:
    1.  prec = precision
    2.  dur = duration
    3.  accel = acceleration
    4.  m = mode quantity
12. var_XXX-*-mem - An experiment for testing variable XXX for peak memory usage
13. var_XXX-kavr_24-pYY-* - An experiment for testing variable XXX using KAVR'24 with precision YY