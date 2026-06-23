# Python API

The HPC Client can be used from Python scripts as well as from the command line.

This is useful for:

- Launching many experiments
- Hyperparameter sweeps
- Reinforcement learning benchmark runs
- Automated evaluation pipelines
- Submitting one job per random seed
- Submitting one job per dataset or configuration

!!! note "Installation"
    The Python API is included in the `hpc_client` package.

    Follow the installation instructions in [Installation](installation.md) to get started.

## Basic Examples

Below is a minimal example of submitting a job from Python.

```python
from hpc_client import HPCClient

client = HPCClient(
    scheduler_url="http://<scheduler-host>:8080",
)

client.login(
    username="<username>",
    password="<password>",
)

job_id = client.submit_job(
    {
        "job_name": "example_job",
        "image": "130.216.238.2:5500/example-image:latest",
        "max_runtime_hours": 1.0,
        "command": None,
        "required_datasets": [],
        "required_worker_ids": [],
    }
)

print(f"Submitted job: {job_id}")
```

!!! note "Security Note" 
    Avoid hard-coding passwords into scripts that are committed to Git.

    Prefer environment variables:

    ```python
    import os

    password = os.environ["HPC_PASSWORD"]
    ```

    Then run:

    ```bash
    export HPC_PASSWORD="<password>"
    python submit_jobs.py
    ```

### List Jobs

```python
jobs = client.list_jobs()

for job in jobs:
    print(job["job_id"], job["status"])
```

### Wait for a Job

```python
client.wait_for_job(job_id)
```

For multiple jobs:

```python
for job_id in job_ids:
    client.wait_for_job(job_id)
    print(f"Finished: {job_id}")
```

### Read Logs

```python
logs = client.get_logs(job_id)

print(logs)
```

### Cancel a Job

```python
client.cancel_job(job_id)
```

## Advanced Examples
These examples demonstrate more complex use cases and best practices for using the Python API to manage HPC jobs.

### Submit and Wait

Example of submitting a job and waiting for it to finish before reading logs.

```python
from hpc_client import HPCClient

client = HPCClient(
    scheduler_url="http://<scheduler-host>:8080",
)

client.login(
    username="<username>",
    password="<password>",
)

job_id = client.submit_job(
    {
        "job_name": "single_training_run",
        "image": "130.216.238.2:5500/my-training-image:latest",
        "max_runtime_hours": 4.0,
        "command": "python train.py",
        "required_datasets": ["project_xyz"],
        "required_worker_ids": [],
    }
)

print(f"Submitted: {job_id}")

client.wait_for_job(job_id)

logs = client.get_logs(job_id)
print(logs)
```

### Small Parameter Sweep

Example of submitting a small hyperparameter sweep with 3 learning rates and 3 seeds each (9 total jobs).

```python
from hpc_client import HPCClient

client = HPCClient(
    scheduler_url="http://<scheduler-host>:8080",
)

client.login(
    username="<username>",
    password="<password>",
)

learning_rates = [1e-3, 3e-4, 1e-4]
seeds = [0, 1, 2]

job_ids = []

for learning_rate in learning_rates:
    for seed in seeds:
        job_name = f"lr_{learning_rate}_seed_{seed}".replace(".", "p")

        command = (
            "python train.py "
            f"--learning-rate {learning_rate} "
            f"--seed {seed}"
        )

        job_id = client.submit_job(
            {
                "job_name": job_name,
                "image": "130.216.238.2:5500/my-training-image:latest",
                "max_runtime_hours": 8.0,
                "command": command,
                "required_datasets": ["project_xyz"],
                "required_worker_ids": [],
            }
        )

        job_ids.append(job_id)
        print(f"Submitted {job_name}: {job_id}")
```

!!! warning "Maximum Job Limit"
    Each user can have a maximum of 50 jobs in the queue to prevent spam.

    If you submit more than 50 jobs, they will be rejected until some of your existing jobs complete or are cancelled.

### Handling Active Job Limits

Each user has a maximum number of active jobs.

Active jobs include:

- queued jobs
- running jobs
- jobs being cancelled
- jobs being deleted
- jobs being preempted

If you submit too many jobs, the scheduler will reject new submissions.

For large sweeps, submit in batches to avoid hitting the limit.

Example:

```python
batch_size = 10

for start in range(0, len(configs), batch_size):
    batch = configs[start : start + batch_size]

    submitted = []

    for config in batch:
        job_id = client.submit_job(config)
        submitted.append(job_id)

    for job_id in submitted:
        client.wait_for_job(job_id)
```



