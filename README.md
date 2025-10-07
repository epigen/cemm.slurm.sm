# Snakemake 8 profile for CeMM's HPC
This is a [global Snakemake profile](https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles) for [CeMM's](https://cemm.at/) SLURM HPC, using the [slurm-executor-plugin](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html). Global Snakemake profiles are the interface between Snakemake workflows and the workload manager of your cluster (here: SLURM).

> [!NOTE]  
> This profile pairs well with workflows from [MrBiomics](https://github.com/epigen/MrBiomics), an effort to augment research by modularizing (biomedical) data science. For more details, instructions, and modules check out the project's repository.


# ⚙️ Setup (one-off)
1. Install the [slurm-executor-plugin](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html#installation)(tested with `v0.10.0`) inside of your existing Snakemake conda environment.
    ```shell
    conda activate snakemake
    conda install snakemake-executor-plugin-slurm
    ```
2. Clone this GitHub repository.
    ```
    git clone https://github.com/epigen/cemm.slurm.sm.git
    ```
3. Adapt the entries in the [config.v8+.yaml](./config.v8+.yaml) to your setup (e.g., put your slurm_account).
4. There are two options to let Snakemake know about the profile:
    -  (Recommended) Set environmental variable, e.g., by adding to `~/.bashrc`, **once**.
    ```
    export SNAKEMAKE_PROFILE=<path/to/this/repo/cemm.slurm.sm>
    ```
    -  Provide it as [Snakemake command line argument](https://snakemake.readthedocs.io/en/stable/executing/cli.html#EXECUTION) with **every** call.
    ```
    snakemake --profile <path/to/this/repo/cemm.slurm.sm>
    ```

# 🛠️ Usage
There are three different flavors depending on personal preference and if the workflow has many jobs to be submitted (hundreds) with "small ones" in the beginning.
- Interactive
    - Start snakemake on your head/login node (recommended by Snakemake developers).
    - This is not allowed at CeMM's HPC.
- Conductor job (recommended)
    - One job (on longq) to rule them all: use a sbatch job script to call and manage (conduct) the execution of all workflow jobs.
    - Set ```immediate-submit: false``` in [config.v8+.yaml](./config.v8+.yaml).
    - For details see next section and [snakejob_conductor.sh](./snakejob_conductor.sh).
    - Advantages
        - Snakemake orchestrates the job submission.
        - One place to check progress, log errors/failed jobs, and document performance (e.g., duration).
    - Disadvantages
        - If the conductor job is canceled the workflow directory might be "locked" → use ```snakemake --unlock```
        - Incomplete files (i.e., files that started to be created, but not finished) might persist → delete the content of this folder ```rm -rf <path/to/workflow>/.snakemake/incomplete/*```
- immediate-submit (not recommended)
    - All jobs will be submitted at once with their respective dependencies, if one job fails all jobs depending on it are cancelled automatically.
    - Set ```immediate-submit: true``` in [config.v8+.yaml](./config.v8+.yaml).
    - Add `--kill-on-invalid-dep=yes` to `slurm_extra` in [config.v8+.yaml](./config.v8+.yaml)..
    - Advantages
        - Everything is submitted at once with SLURM dependencies.
        - Maximum parallelization is achieved.
    - Disadvantages:
        - An error is thrown if a job with a dependency gets submitted, but the dependency has already finished. This can happen if early jobs are very small.
        - To find failed jobs one has to investigate many `.log` files and/or look at the remaining/unfinished jobs in a new Snakemake DAG.
        - If you submit a lot of jobs (e.g., >500) this might take some time (i.e., 1s/job) until all jobs are submitted.
    - Open question: behaviour of ```--retries``` flag unknown. If someone finds out, please let me know.


# 🐍 Snakejob Conductor
If you want to use a conductor job for the submission and execution of your worklfow follow these steps:
1. Copy ```snakejob_conductor.sh``` to the workflow/project root directory.
2. Go through every line and adapt it according to your setup (e.g., set paths to the log folder and use absolute paths).
3. Use ```sbatch snakejob_conductor.sh``` to submit the conductor job.
4. Watch the queue and/or check the .out/.err files for progress. A useful script to parse conductor-generated logfiles is `parse_errors.py`. This script counts the types of errors & sorts the file paths by them in an easily copy-pasteable way (optimized for snakemake v9). It works if your logging directories always have the same structure, e.g., you save them in `~/projects/*/results/logs/snake_sbatch/*conductor*.out`

# ℹ️ Job Information
The SLURM job's comments contain the `rule` and `wildcard` information and can be accessed using `%.50k` in `squeue`:
```
squeue -u $USER -o %i,%P,%.50j,%.50k
```

You can also create an `alias` for checking on all your jobs in a structured manner.
```
alias mq="squeue -u sreichl -o '%.22i %.9P %.50j %.50k %.8u %.2t %.10M %.4C %.9m %.6D %R'"
```

# 🗒️ Job Logs
Snakemake will print the following upon SLURM job submissions, pointing to the respective SLURM job log files containing standard output:
```
Job {XX} has been submitted with SLURM jobid {jobid} (log: /path/to/workflow/.snakemake/slurm_logs/rule_{rulename}/{wildcards}/{jobid}.log).
```

# MedUni HPC cluster

For a similar profile working for the MedUni HPC cluster, refer to https://github.com/moritzschaefer/muwhpc_slurm
