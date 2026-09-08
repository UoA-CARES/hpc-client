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

!!! note "Runtime Limits Affect Opportunistic Scheduling"

    The requested runtime also affects how jobs can use spare cluster capacity.

    Jobs requesting **24 hours or less** can run opportunistically without being automatically preempted.

    Jobs requesting **more than 24 hours** must be submitted as resumable if they are to run outside your Normal and Overflow allocation. 

    See [Job Priorities and Scheduling Tiers](scheduling.md) for the full scheduling rules.

### Save Outputs and Checkpoints Frequently

Long-running jobs should periodically save:

- checkpoints
- models
- metrics
- training progress
- other important state

to:

```text
/workspace/output
```

For workloads that can recover from checkpoints, submit the job with:

```json
"resumable": true
```

Resumable jobs can recover after unexpected worker or machine interruptions and can also safely participate in resumable Opportunistic scheduling.

When a resumable job starts again, previously saved files may already exist under:

```text
/workspace/output
```

Your code must detect and reload its own checkpoint.

A good pattern is:

```python
from pathlib import Path

checkpoint = Path("/workspace/output/checkpoints/latest.pt")

if checkpoint.exists():
    # Restore model, optimiser, training step, etc.
    ...
else:
    # Start from scratch.
    ...
```

Save checkpoints frequently enough that an interruption or preemption does not cause a large amount of computation to be repeated.

!!! important "Recommended for Long Jobs"

    If a job may require more than 24 hours, making it resumable is strongly recommended.

    Long non-resumable jobs outside your Normal and Overflow allocation are Held rather than being allowed to use Opportunistic capacity.

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