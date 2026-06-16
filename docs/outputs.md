# Outputs

Outputs are the files produced by your job.

Examples include:

- Trained models
- Checkpoints
- Evaluation results
- CSV files
- Images and plots
- Videos
- Reports
- Generated datasets

## Output Directory

All files that should be preserved after a job completes must be written to:

```text
/workspace/output
```

Anything written to this directory is automatically copied back to HPC storage when the job finishes.

Example:

```python
from pathlib import Path

output_dir = Path("/workspace/output")
output_dir.mkdir(parents=True, exist_ok=True)

(output_dir / "results.txt").write_text(
    "Training completed successfully\n",
    encoding="utf-8",
)
```

!!! warning "Containers Are Temporary"

    Docker containers are non-persistent.

    Any files written inside the container will be lost when the job finishes.

    Save all results to:

    ```text
    /workspace/output
    ```

    Files written to this directory are copied back to the HPC storage and remain available after the job completes.

!!! warning "Outputs Must Be Saved to the Correct Path"

    You are responsible for ensuring all of your code saves outputs to:

    ```text
    /workspace/output
    ```

    If files are written somewhere else, they will be lost when the container is removed.

## What Gets Saved

Files written inside:

```text
/workspace/output
```

are preserved.

Example:

```text
/workspace/output
├── model.pt
├── metrics.csv
└── figures
    └── reward_curve.png
```

These files will be available after the job completes.

## What Does Not Get Saved

Files written elsewhere inside the container are temporary.

Example:

```text
/app
/tmp
/home
```

Data written to these locations will be lost when the container exits.

Example:

```python
Path("/tmp/results.txt").write_text("data")
```

This file will disappear when the job finishes.

Always save important files into:

```text
/workspace/output
```

## Recommended Output Structure

For larger projects, organise outputs into folders.

Example:

```text
/workspace/output
├── checkpoints
├── figures
├── logs
├── models
└── results
```

Example:

```python
from pathlib import Path

output_dir = Path("/workspace/output")

(output_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
(output_dir / "models").mkdir(parents=True, exist_ok=True)
(output_dir / "results").mkdir(parents=True, exist_ok=True)
```

!!! warning "Output Structure"

    The directory structure created inside the container is preserved when the job finishes.

    If you create a messy output structure, it will be preserved as-is.

    Organise outputs into directories to make them easier to browse and analyse.

!!! warning "Code Responsibility"

    You are responsible for ensuring your code saves outputs to the correct path and handles any necessary directory creation.

    The HPC system does not automatically create subdirectories inside:

    ```text
    /workspace/output
    ```

    If you want to save files into subdirectories, your code needs to create those directories first.

## Accessing Outputs

After a job completes, outputs are available from the shared HPC storage under:

```text
/cares-nas/hpc/outputs/<upi>/<job_id>
```

The scheduler preserves the directory structure created inside:

```text
/workspace/output
```

For example:

```text
/workspace/output
├── models
│   └── model.pt
└── results
    └── metrics.csv
```

will appear in the final job outputs exactly as written.

!!! info "Private Access"

    Output directories are private to each user.

    You cannot access outputs from other users' jobs.

## Outputs vs Logs

Outputs and logs serve different purposes.

| Type | Purpose |
|--------|--------|
| Logs | Progress updates, debugging information, status messages |
| Outputs | Models, checkpoints, CSV files, figures, reports, videos |

Example:

```python
print("Training complete")
```

appears in the logs.

Example:

```python
torch.save(
    model.state_dict(),
    "/workspace/output/models/model.pt",
)
```

creates a saved output file.

## Viewing Logs

Logs can be viewed using:

```bash
hpc-client logs <job_id>
```

Use logs to monitor progress while a job is running.

## Large Outputs

Large outputs are supported, however users should:

- Remove unnecessary files
- Avoid storing temporary data
- Compress outputs where appropriate
- Delete old outputs when no longer required

## Common Mistakes

??? failure "Outputs Missing"

    Files were written outside:

    ```text
    /workspace/output
    ```

??? failure "Empty Output Directory"

    Verify files were actually created.

    Example:

    ```python
    output_dir.mkdir(parents=True, exist_ok=True)
    ```

??? failure "Only Logs Exist"

    Printing information does not create output files.

    Example:

    ```python
    print("Training complete")
    ```

    creates log messages but does not save any files.

??? failure "Output Structure Is Messy"

    Organise outputs into directories:

    ```text
    checkpoints/
    figures/
    models/
    results/
    ```

    to make outputs easier to browse and analyse.

## Recommended Workflow

```python
from pathlib import Path

output_dir = Path("/workspace/output")

(output_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
(output_dir / "models").mkdir(parents=True, exist_ok=True)
(output_dir / "results").mkdir(parents=True, exist_ok=True)
(output_dir / "figures").mkdir(parents=True, exist_ok=True)
```

Keep all final artefacts inside:

```text
/workspace/output
```

to ensure they are preserved after the job completes.