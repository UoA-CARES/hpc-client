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

### What Gets Saved

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

### What Does Not Get Saved

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

### Recommended Output Structure

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

## Accessing Job Outputs from the NAS

Job outputs are stored on the CARES NAS and can be accessed directly from your computer.

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

---

### Downloading Outputs (UI)

To download outputs, navigate to the `outputs/<upi>` folder at: [http://130.216.238.2:5000](http://130.216.238.2:5000). Click on the relevant job folder to download the outputs as a zip file.

### Mounting the Output Directory (Linux)

Mounting the NAS locally is often more convenient than downloading files through a web browser, especially for large datasets, model checkpoints, videos, and experiment results.

Create a local mount point:

```bash
mkdir -p ~/hpc_outputs
```

Mount the NAS:

```bash
sudo mount -t cifs \
    //130.216.238.2/outputs/<upi> \
    ~/hpc_outputs \
    -o username=<upi>
```

Example:

```bash
sudo mount -t cifs \
    //130.216.238.2/outputs \
    ~/hpc_outputs/jsmith123 \
    -o username=jsmith123
```

You will be prompted for your NAS password.

---

#### Accessing Your Outputs

After mounting:

```bash
cd ~/hpc_outputs
```

Browse your output directory:

```bash
cd jsmith123
```

Example:

```text
~/hpc_outputs/jsmith123/
├── job_001/
├── job_002/
├── job_003/
└── ...
```

---

#### Copying Results

Copy a job locally:

```bash
cp -r \
    ~/hpc_outputs/jsmith123/job_001 \
    ~/Downloads/
```

Copy an individual file:

```bash
cp \
    ~/hpc_outputs/jsmith123/job_001/results.csv \
    .
```

---

#### Unmounting

When finished:

```bash
sudo umount ~/hpc_outputs
```

---

#### Using rsync

For large results it is often more efficient to use `rsync`.

Example:

```bash
rsync -avP \
    ~/hpc_outputs/jsmith123/job_001/ \
    ./job_001/
```

This allows interrupted transfers to resume.

---

### Recommended Workflow

```text
Run Job
    ↓
Monitor Job
    ↓
Job Completes
    ↓
Mount NAS
    ↓
Copy Results Locally
    ↓
Analyse Results
```

For large machine learning experiments, model checkpoints, videos, and datasets, mounting the NAS is generally the easiest way to access your results.


### Outputs vs Logs

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

### Large Outputs

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

