#!/bin/bash
#SBATCH --output </path/to/logs/>snakejob_conductor_%j.log # log file location (stdout), %j stands for unique job ID
#SBATCH --job-name=analysis_project_name
#SBATCH --partition=longq # job queue where the job is submitted to
#SBATCH --qos=longq # qos must match the partition
#SBATCH --nodes=1 # number of physical nodes
#SBATCH --ntasks=1 # 1 task
#SBATCH --cpus-per-task=1 # 1 task on 1 CPU
#SBATCH --time=16:00:00
# Optional parameters
#SBATCH --mem=1000 # using 1Gb of memory
#SBATCH --error </path/to/logs/>snakejob_conductor_%j.err # error log file location (stderr), %j stands for unique job ID
#SBATCH --mail-type=end # send an email when this job ends
#SBATCH --mail-user=<username>@cemm.at # email your CeMM account

# (Optional) Examples of the Slurm environmental variables. Provide additional information
echo "======================"
echo $SLURM_SUBMIT_DIR
echo $SLURM_JOB_NAME
echo $SLURM_JOB_PARTITION
echo $SLURM_NTASKS
echo $SLURM_NPROCS
echo $SLURM_JOB_ID
echo $SLURM_JOB_NUM_NODES
echo $SLURM_NODELIST
echo $SLURM_CPUS_ON_NODE
echo "======================"

# *** setup environment ***
# soruce conda and activate your Snakemake environment
source <path/to/conda>/miniconda3/etc/profile.d/conda.sh
conda activate <snakemake_environment_name>

# change directory to workflow/project
cd <path/to/workflow>

# *** start the workflow ***
date
snakemake -p --use-conda
# snakemake --report <path/to/report.html/zip>
date

