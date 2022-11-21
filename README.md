# CeMM's Snakemake SLURM cluster profile
Snakemake SLURM cluster profile for the HPC at [CeMM](https://cemm.at/) based on the [SLURM cookicutter repository](https://github.com/Snakemake-Profiles/slurm).
[Snakemake (cluster) profiles](https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles) are the interface between Snakemake workflows and the workload manager of your cluster.

# Setup
1. clone this GitHub repository
2. adapt the entries in the config.yaml to your setup (e.g., put the correct path to slurm_submit.py)
3. use it as explained below

# Usage
There are two options for the use of this cluster profile with any snakemake workflow.

-  (recommended) Set environmental variable (e.g., put in bashrc **once**) 
```
export SNAKEMAKE_PROFILE=<path/to/this/repo>
```

-  Use it as [Snakemake command line parameter:](https://snakemake.readthedocs.io/en/stable/executing/cli.html#EXECUTION) (**everytime**)
```
snakemake --profile <path/to/this/repo>
```

# Configuration
There are two different configuration/submission flavors depending on personal preference and if the workflow has many jobs to be submitted (hundreds) with "small ones" in the beginning
- immediate-submit
    - set ```immediate-submit: true``` in config.yaml
    - all jobs will be submitted at once with their respective dependencies, if one job fails all jobs depending on it are cancelled automatically
    - advantages
        - everything is submitted at once with dependencies
        - maximum parallelization is achieved
    - disadvanatges:
        - an error is triggered if a job with a dependency gets submitted, but the dependency has already finished
        - to find failed jobs one has to investigate many .err files and/or look at the remaining/unfinished jobs in a new Snakemake DAG
    - open question: behaviour of ```--retries``` flag unknown. If someone finds out, please let me know.
- Conductor job (for details see snakejob_conductor.sh)
    - one job (on longq) to rule them all: use a sbatch job script to call and manage (conduct) the execution of all workflow jobs
    - set ```immediate-submit: false``` in config.yaml
    - advantages
        - snakemake orchestrates the job submission
        - one place to check progress, log errors/failed jobs, and document performance (e.g., duration)
    - disadvanatges:
        - if the conductor job is canceled the workflow directory might be "locked" → use ```snakemake --unlock```
        - incomplete files (i.e., files that started to be created, but not finished) might persist → delete the content of this folder ```rm -rf <path/to/workflow>/.snakemake/incomplete/*```

# Snakejob Conductor (recommended for powerusers)
If you want to use a conductor job for the submission and execution of a worklfow follow these steps:
1. copy ```snakejob_conductor.sh``` to the workflow/project root directory
2. go through every line and adapt it according to your setup (e.g., set paths to the log folder and use absolute paths)
3. use ```sbatch snakejob_conductor.sh``` to submit the conductor job
4. watch the queue and/or check the .out/.err files for progress
