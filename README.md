# HPC Client

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://uoa-cares.github.io/hpc-client/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

Command-line client for submitting Docker jobs to the CARES HPC Scheduler.

The HPC Client lets students and researchers:

- Log in to the scheduler
- Submit jobs
- List jobs
- Wait for jobs to finish
- View logs
- Cancel jobs

## Training Cluster, not a Dvelopment Environment
The CARES HPC cluster is designed for running complete workloads, not for interactive software development.

Before submitting a job you should:

- Develop and test your code locally
- Build a Docker image containing all required code and dependencies
- Verify the Docker image runs correctly on your own machine
- Upload any required datasets to the CARES NAS
- Submit the job to the scheduler

Jobs should be self-contained and executable without manual intervention.

## Account Required

You cannot create your own account through the client.

Contact the HPC administrators on the UoA-CARES slack and request an account before using the HPC Client.

Provide:

- Your UPI
- Your University of Auckland email address
- Your name
- Your supervisor name
- A short description of the work you want to run

## Full Documentation

The full documentation is available at [https://uoa-cares.github.io/hpc-client/](https://uoa-cares.github.io/hpc-client/).

The documentation includes:
- Installation instructions
- Job Configuration
- Docker Image Management
- Dataset Management
- Output Management
- Troubleshooting tips

## Installation

```bash
git clone git@github.com:UoA-CARES/hpc-client.git
cd hpc-client

python -m venv .venv
source .venv/bin/activate

pip install -e .
```

## Configure Scheduler

```bash
hpc-client configure \
    --scheduler-url http://<scheduler-host>:8080
```

## Login

```bash
hpc-client login <username>
```

## Create a Job

Create `job.json`:

```json
{
  "job_name": "count_to_60",
  "image": "130.216.238.2:5500/count-to-60:latest",
  "max_runtime_hours": 1.0,
  "command": null,
  "required_datasets": [],
  "required_worker_ids": []
}
```

## Submit a Job

```bash
hpc-client submit job.json
```

Example output:

```text
count_to_60_260616120000_abcd
```

## Monitor Jobs

List jobs:

```bash
hpc-client jobs
```

Wait for completion:

```bash
hpc-client wait <job_id>
```

View logs:

```bash
hpc-client logs <job_id>
```

Cancel a job:

```bash
hpc-client cancel <job_id>
```

## Datasets

Datasets are stored on the CARES NAS.

Reference datasets by name:

```json
{
  "required_datasets": [
    "project_xyz"
  ]
}
```

Inside the container:

```text
/workspace/datasets/project_xyz
```

## Outputs

Save outputs to:

```text
/workspace/output
```

Anything written to this directory is preserved after the job completes.

Example:

```python
from pathlib import Path

output_dir = Path("/workspace/output")
output_dir.mkdir(parents=True, exist_ok=True)

(output_dir / "results.txt").write_text(
    "Training complete\n",
    encoding="utf-8",
)
```

## Typical Workflow

```bash
hpc-client login <username>

hpc-client submit job.json

hpc-client jobs

hpc-client logs <job_id>

hpc-client wait <job_id>
```

## Submitting Jobs from Python

The HPC Client can be used directly from Python scripts.

This is useful when:

- Launching multiple experiments
- Hyperparameter sweeps
- Reinforcement learning benchmark runs
- Automated evaluation pipelines

Example:

```python
from hpc_client import HPCClient

client = HPCClient(
    scheduler_url="http://scheduler.example.nz:8080"
)

client.login(
    username="abc123",
    password="your_password",
)

job_id = client.submit_job(
    {
        "job_name": "experiment_001",
        "image": "130.216.238.2:5500/my-project:latest",
        "max_runtime_hours": 4.0,
        "command": "python train.py --seed 1",
        "required_datasets": ["project_xyz"],
        "required_worker_ids": [],
    }
)

print(f"Submitted: {job_id}")
```

### Launch Multiple Jobs

```python
from hpc_client import HPCClient

client = HPCClient(
    scheduler_url="http://scheduler.example.nz:8080"
)

client.login(
    username="abc123",
    password="your_password",
)

for seed in range(10):
    job_id = client.submit_job(
        {
            "job_name": f"ppo_seed_{seed}",
            "image": "130.216.238.2:5500/ppo:latest",
            "max_runtime_hours": 12.0,
            "command": f"python train.py --seed {seed}",
            "required_datasets": ["project_xyz"],
            "required_worker_ids": [],
        }
    )

    print(f"Submitted {job_id}")
```

### Monitoring Jobs

```python
jobs = client.list_jobs()

for job in jobs:
    print(
        job["job_id"],
        job["status"],
    )
```

### Waiting for Completion

```python
client.wait_for_job(job_id)
```

### Retrieving Logs

```python
logs = client.get_logs(job_id)

print(logs)
```

Using the Python API allows entire experiment suites to be submitted and managed programmatically without manually creating and submitting individual `job.json` files.