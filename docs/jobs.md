# Jobs

Jobs are submitted using a JSON job file.

A job file tells the scheduler:

- which Docker image to run
- how long the job is allowed to run
- which datasets are required
- whether the job needs a specific worker
- what command to run inside the container

## Minimal job.json

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

The command returns a job ID.

Example:

```text
count_to_60_260615151441_168b
```

## List Jobs

```bash
hpc-client jobs
```

Common statuses:

| Status | Meaning |
|----------|----------|
| queued | Waiting for a worker |
| running | Currently running |
| completed | Finished successfully |
| failed | Finished with an error |
| cancelled | Cancelled before or during execution |

## Wait for Completion

```bash
hpc-client wait <job_id>
```

## View Logs

```bash
hpc-client logs <job_id>
```

Anything written to standard output inside the container is available through the logs.

Example:

```python
print("Training started")
print("Epoch 1")
print("Finished")
```

## Cancel a Job

```bash
hpc-client cancel <job_id>
```

Queued jobs are cancelled immediately.

Running jobs are terminated on the worker.

## job.json Fields

### job_name

Human-readable name for the job.

```json
"job_name": "training_run_seed_1"
```

Examples:

```text
mnist_seed_1
ppo_ball_in_cup_seed_3
resnet50_baseline
```

### image

Docker image to run.

CARES Registry example:

```json
"image": "130.216.238.2:5500/count-to-60:latest"
```

Docker Hub example:

```json
"image": "python:3.11-slim"
```

If no registry address is supplied, Docker attempts to pull the image from Docker Hub.

### max_runtime_hours

Maximum runtime in hours.

```json
"max_runtime_hours": 4.0
```

If a job exceeds this runtime, the worker terminates the container.

Examples:

| Value | Runtime |
|---------|---------|
| 0.5 | 30 minutes |
| 1.0 | 1 hour |
| 4.0 | 4 hours |
| 12.0 | 12 hours |

### command

Optional command override.

Use the Docker image default command:

```json
"command": null
```

Override the command:

```json
"command": "python train.py --seed 1"
```

The command runs inside the container.

### required_datasets

List of datasets required by the job.

No datasets:

```json
"required_datasets": []
```

One dataset:

```json
"required_datasets": ["mnist"]
```

Multiple datasets:

```json
"required_datasets": ["mnist", "cifar10"]
```

Datasets are mounted read-only inside the container:

```text
/workspace/datasets/<dataset_name>
```

Example:

```text
/workspace/datasets/mnist
```

### required_worker_ids

Normally leave empty:

```json
"required_worker_ids": []
```

Only use this when instructed by an administrator.

Example:

```json
"required_worker_ids": ["gpu01"]
```

## Example: Default Docker Command

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

## Example: Dataset Job

```json
{
  "job_name": "mnist_training",
  "image": "130.216.238.2:5500/mnist-training:latest",
  "max_runtime_hours": 4.0,
  "command": null,
  "required_datasets": ["mnist"],
  "required_worker_ids": []
}
```

Inside the container:

```text
/workspace/datasets/mnist
```

## Runtime Limits

Jobs must complete within:

```json
"max_runtime_hours"
```

If a job exceeds the limit:

- the container is terminated
- the job is marked as failed
- logs remain available
- saved outputs remain available
- the worker becomes available for another job

## Active Job Limits

Each user has a maximum number of active jobs.

Active jobs include:

- queued
- running
- cancelling
- deleting
- preempting

If the limit is reached, new job submissions are rejected until existing jobs complete or are cancelled to be below the limit.

## Recommended Workflow

```bash
hpc-client submit job.json
hpc-client jobs
hpc-client wait <job_id>
hpc-client logs <job_id>
```

For long-running jobs:

```bash
hpc-client logs <job_id>
```

to monitor progress.

## Common Mistakes

??? failure "Job never starts"

    All workers may currently be busy.

    Check:

    ```bash
    hpc-client jobs
    ```

??? failure "Image cannot be pulled"

    Check the image name.

    Registry:

    ```text
    130.216.238.2:5500/count-to-60:latest
    ```

    Docker Hub:

    ```text
    python:3.11-slim
    ```

??? failure "Dataset not found"

    Check:

    ```json
    "required_datasets": ["dataset_name"]
    ```

??? failure "Outputs missing"

    Save files into:

    ```text
    /workspace/output
    ```

    Files written elsewhere may be lost when the container exits.