# Troubleshooting and Best Practices
Below are some tips to help you get the most out of the HPC Scheduler.

## Best Practices
Below a few tips to help you get the most out of the HPC Scheduler.

### Submit Meaningful Job Names

Use names that identify the experiment.

Good:

```text
ppo_seed_1
resnet_lr_1e3_seed_2
dataset_ablation_seed_0
```

Poor:

```text
test
job
run
new
```

### Use Realistic Runtime Limits

Example:

```json
"max_runtime_hours": 4.0
```

Jobs exceeding their runtime limit are automatically terminated.

### Save Outputs and Checkpoints Frequently

Long-running jobs should periodically save:

- checkpoints
- models
- metrics
- other important progress

to:

```text
/workspace/output
```

For workloads that support checkpoint recovery, consider submitting the job with:

```json
"resumable": true
```

A resumable job may be restarted after an unexpected worker or machine interruption with its existing `/workspace/output` directory preserved.

Your code must still detect and reload its own checkpoint when it starts.

A good pattern is:

```python
from pathlib import Path

checkpoint = Path("/workspace/output/checkpoints/latest.pt")

if checkpoint.exists():
    # restore previous state
    ...
else:
    # start from scratch
    ...
```

Save checkpoints frequently enough that restarting the job does not lose a large amount of computation.

### Organise Outputs

Use:

```text
checkpoints/
figures/
models/
results/
```

rather than placing everything in a single directory.

### Keep Images Small

Smaller images start faster.

Avoid installing unnecessary packages.

### Test Locally First

Always verify:

```bash
docker run --rm image_name
```

before submitting a large job.

### Use Command Overrides for Sweeps

Build one Docker image and vary jobs run using override commands:

```json
"command": "python train.py --seed 1"
```

This avoids rebuilding the image for every experiment.

### Avoid Submitting Thousands of Jobs at Once

Submit large sweeps in batches.

This keeps the queue manageable and avoids hitting your active job limit.

!!! warning "Maximum Job Limit"
    Each user can have a maximum of 50 jobs in the queue to prevent spam.

    If you submit more than 50 jobs, they will be rejected until some of your existing jobs complete or are cancelled.

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