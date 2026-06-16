# User Guide

This quick guide walks through the complete workflow for running jobs on the CARES HPC cluster.

By the end of this guide you will know how to:

- Access the HPC system
- Upload datasets
- Build Docker images
- Submit jobs
- Monitor progress
- Retrieve results
- Automate experiment submission using Python

Specific details about each section can be found in the corresponding documentation pages:

- [Job Management](jobs.md)
- [Docker Images](docker.md)
- [Datasets](datasets.md)
- [Outputs](outputs.md)

!!! info "HPC Client Documentation"

    This guide is a high-level overview.

    For detailed instructions and troubleshooting tips, refer to the full documentation.

## Overview

The HPC Scheduler executes Docker containers on a pool of worker machines.

The typical workflow is:

```text
Write Code
    ↓
Build Docker Image
    ↓
Push Image
    ↓
Upload Dataset
    ↓
Submit Job
    ↓
Monitor Logs
    ↓
Collect Results
```

!!! warning "Not for Interactive Workloads"
    The CARES HPC cluster is designed for running completed workloads, not for interactive software development.

    Before submitting a job you should:

    - Develop and test your code locally
    - Build a Docker image containing all required code and dependencies
    - Verify the Docker image runs correctly on your own machine
    - Upload any required datasets to the CARES NAS
    - Submit the job to the scheduler

## Step 1: Request an Account

Accounts are created by the HPC administrators.

Users cannot create their own accounts.

Contact the administrators and provide:

- Name - first and last
- UPI
- University email address
- Supervisor name
- Intended HPC usage

Once your account has been created you can log in to the scheduler.

## Step 2: Configure the Client

Configure the scheduler URL:

```bash
hpc-client configure \
    --scheduler-url http://<scheduler-host>:8080
```

Login:

```bash
hpc-client login <username>
```

Verify:

```bash
hpc-client whoami
```

## Step 3: Build a Docker Image

Example project:

```text
project/
├── Dockerfile
└── main.py
```

Example:

```python
import pathlib
import time

output_dir = pathlib.Path("/workspace/output")
output_dir.mkdir(parents=True, exist_ok=True)

for i in range(60):
    print(f"Count: {i}")
    time.sleep(1)

(output_dir / "result.txt").write_text(
    "Finished successfully\n",
    encoding="utf-8",
)
```

Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY main.py .

CMD ["python", "main.py"]
```

Build:

```bash
docker build -t count-to-60:latest .
```

Test locally:

```bash
docker run --rm count-to-60:latest
```

!!! warning "Code Must Be in the Docker Image"

    The HPC Scheduler only runs code that is included in your Docker image.

    You cannot run arbitrary commands on the worker machines.

    If you want to run a script, it must be included in the image and specified as the entry point.

!!! warning "Job Must Be Self-Contained"
    Jobs should be self-contained and executable without manual intervention.

    A submitted Docker image should contain everything required to perform the task:

    - Source code
    - Python packages
    - System dependencies
    - Configuration files
    - Training scripts
    - Evaluation scripts

## Step 4: Push the Image

Tag:

```bash
docker tag \
    count-to-60:latest \
    130.216.238.2:5500/count-to-60:latest
```

Push:

```bash
docker push \
    130.216.238.2:5500/count-to-60:latest
```

Verify:

```bash
docker pull \
    130.216.238.2:5500/count-to-60:latest
```

!!! warning "Trust Docker Registry"
    See [Docker Registry Configuration](docker.md#docker-registry-configuration) for instructions on how to add the HPC Docker registry to your trusted registry list.

    This only needs to be configured once per machine.

    After the registry has been added to Docker's trusted registry list, images can be pushed and pulled normally.

## Step 5: Upload a Dataset

Datasets are stored on the shared CARES NAS.

Create a dataset directory:

```text
datasets/
└── project_xyz
```

Upload your files:

```text
datasets/
└── project_xyz
    ├── train
    ├── test
    └── metadata.csv
```

The directory name becomes the dataset name.

Example:

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

## Step 6: Create a Job

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

Submit:

```bash
hpc-client submit job.json
```

Example output:

```text
count_to_60_260616120000_abcd
```

## Step 7: Monitor the Job

List jobs:

```bash
hpc-client jobs
```

View logs:

```bash
hpc-client logs <job_id>
```

Wait for completion:

```bash
hpc-client wait <job_id>
```

Cancel a job:

```bash
hpc-client cancel <job_id>
```

## Step 8: Retrieve Results

Anything written to:

```text
/workspace/output
```

is preserved.

Example:

```python
(output_dir / "metrics.csv").write_text(
    "episode,reward\n1,123\n",
    encoding="utf-8",
)
```

Recommended structure:

```text
/workspace/output
├── checkpoints
├── figures
├── models
└── results
```

Results are available after the job completes through the shared HPC storage.

## Logs vs Outputs

Logs:

```python
print("Epoch 1")
print("Epoch 2")
```

View using:

```bash
hpc-client logs <job_id>
```

Outputs:

```python
torch.save(
    model.state_dict(),
    "/workspace/output/models/model.pt",
)
```

are preserved after the job completes.

## Running Many Experiments

For parameter sweeps and benchmarking, create multiple jobs.

Example:

```json
{
  "job_name": "ppo_seed_1",
  "image": "130.216.238.2:5500/ppo:latest",
  "max_runtime_hours": 12.0,
  "command": "python train.py --seed 1",
  "required_datasets": ["project_xyz"],
  "required_worker_ids": []
}
```

Create one job per seed:

```text
ppo_seed_1
ppo_seed_2
ppo_seed_3
ppo_seed_4
ppo_seed_5
```

This allows the scheduler to run experiments in parallel across multiple workers.

## Submitting Jobs from Python

The client can also be used directly from Python.

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

print(job_id)
```

This is useful for:

- Hyperparameter sweeps
- Reinforcement learning benchmarks
- Automated evaluation pipelines
- Batch experiment submission

## Best Practices

### Keep Images Small

Smaller images start faster.

Avoid installing unnecessary packages.

### Use Realistic Runtime Limits

Example:

```json
"max_runtime_hours": 4.0
```

Jobs exceeding their runtime limit are automatically terminated.

### Save Outputs Frequently

Long-running jobs should periodically save:

- checkpoints
- models
- metrics

to:

```text
/workspace/output
```

### Organise Outputs

Use:

```text
checkpoints/
figures/
models/
results/
```

rather than placing everything in a single directory.

### Test Locally First

Always verify:

```bash
docker run --rm image_name
```

before submitting a large job.

## Troubleshooting

??? failure "Job Never Starts"

    Workers may be busy.

    Check:

    ```bash
    hpc-client jobs
    ```

??? failure "Dataset Not Found"

    Verify the dataset exists on the CARES NAS.

??? failure "Image Cannot Be Pulled"

    Verify the image name and tag.

??? failure "Outputs Missing"

    Ensure outputs are written to:

    ```text
    /workspace/output
    ```

??? failure "Job Timed Out"

    Increase:

    ```json
    "max_runtime_hours"
    ```

    if the job genuinely requires more runtime.