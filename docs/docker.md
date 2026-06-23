# Docker Images

All jobs submitted to the HPC Scheduler run inside Docker containers.

Your Docker image contains:

* Your code
* Python packages
* System dependencies
* Entry point

The scheduler launches your image on an available worker and captures the outputs.

## Important Concepts

!!! info "Code Must Be in the Docker Image"

    The HPC Scheduler only runs code that is included in your Docker image.

    You cannot run arbitrary commands on the worker machines.

    If you want to run a script, it must be included in the image and specified as the entry point.

!!! info "Docker Images Must Be Self-Contained"
    Docker images should be self-contained and executable without manual intervention.

    A submitted Docker image should contain everything required to perform the task:

    - Source code
    - Python packages
    - System dependencies
    - Configuration files
    - Training scripts
    - Evaluation scripts

!!! warning "Do not store Datasets in Docker Images"

    Datasets should not be included in Docker images.

    Instead, upload datasets to the CARES NAS and request them in `job.json`.

    Requested datasets are mounted read-only inside the container at:

    ```text
    /workspace/datasets/<dataset_name>
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

!!! info "Datasets Are Mounted Automatically"

    Datasets requested in `job.json` are mounted **read-only** at:

    ```text
    /workspace/datasets/<dataset_name>
    ```

    Example:

    ```text
    /workspace/datasets/mnist
    /workspace/datasets/cifar10
    ```

    Do not attempt to modify dataset contents.

## Designing Docker Images for HPC Jobs

Unlike a traditional server, virtual machine or development environment, Docker images submitted to the HPC Scheduler should be designed as complete workloads that can execute automatically from start to finish.

A useful way to think about a Docker image is:

```text
Docker Image = Executable Program
```

When a job starts, the scheduler:

```text
Pull Image
    ↓
Start Container
    ↓
Run Command
    ↓
Save Outputs
    ↓
Stop Container
```

Users are not able to: 

- SSH into containers
- Install packages manually
- Edit source code inside containers
- Start training interactively
- Leave containers running indefinitely

Instead, the image should already contain everything required to perform the task.

!!! warning "Do Not Compile Datasets into Docker Images"

    Datasets should **NOT** be included in Docker images.

    Instead, upload datasets to the CARES NAS and request them in the job submission.

    Requested datasets are mounted read-only inside the container at:

    ```text
    /workspace/datasets/<dataset_name>
    ```

### A Good HPC Docker Image

A good HPC image:

```text
Contains:
    Code
    Dependencies
    Configuration

Starts:
    Automatically

Runs:
    Without User Interaction

Produces:
    Outputs

Exits:
    Cleanly
```

Example workflow:

```text
Load Dataset
    ↓
Train Model
    ↓
Evaluate Model
    ↓
Save Results
    ↓
Exit
```

### A Poor HPC Docker Image

The following pattern is not recommended:

```text
Start Container
    ↓
Wait For User
    ↓
SSH Into Container
    ↓
Install Packages
    ↓
Edit Code
    ↓
Start Training
```

This is a development workflow rather than an HPC workflow.

Development should occur on your local machine before creating the Docker image.

### Keep Images Reproducible

The same Docker image should be able to run repeatedly and produce consistent results.

A good image contains:

- Source code
- Python packages
- System dependencies
- Configuration files
- Training scripts
- Evaluation scripts

Everything required to execute the workload should already be present in the image.

!!! warning "Do Not Compile Datasets into Docker Images"

    Datasets should **NOT** be included in Docker images.

    Instead, upload datasets to the CARES NAS and request them in the job submission.

    Requested datasets are mounted read-only inside the container at:

    ```text
    /workspace/datasets/<dataset_name>
    ```

### Use Environment Variables and Arguments

Avoid hard-coding experiment settings.

Instead:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int)

args = parser.parse_args()
```

Then override parameters using the job command:

```json
{
  "command": "python train.py --seed 42"
}
```

This allows a single image to be reused for many experiments.

!!! info "Data Paths Should Be Configurable"

    Do not hard-code dataset paths.

    Use environment variables or command-line arguments to specify where data is saved and stored. 

    Configure all output paths to point to:

    ```text
    /workspace/output
    ```

    inside of the Docker container.    

### Save Outputs Explicitly

Anything you want to keep must be written to:

```text
/workspace/output
```

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

Files written elsewhere may be lost when the container exits.

!!! info "Outputs Are Saved Automatically"

    Anything written to:

    ```text
    /workspace/output
    ```

    is automatically saved by the scheduler and copied back to the HPC storage when the job finishes.

    Anything else inside the container is temporary and will be lost when the container exits.

### Use Mounted Datasets

Datasets requested in:

```json
"required_datasets"
```

are mounted automatically inside the container:

```text
/workspace/datasets/<dataset_name>
```

Your image should expect datasets to appear there.

Example:

```python
from pathlib import Path

dataset_root = Path("/workspace/datasets/project_xyz")
```

!!! info "Datasets Should Not Be Included in Docker Images"

    Datasets should not be included in Docker images.

    Instead, upload datasets to the CARES NAS and request them in `job.json`.

    Requested datasets are mounted read-only inside the container at:

    ```text
    /workspace/datasets/<dataset_name>
    ```

### Test Locally First

Before pushing an image and submitting a job:

```bash
docker build -t my-image .
docker run --rm my-image
```

The container should:

1. Start successfully
2. Complete the workload
3. Produce outputs
4. Exit cleanly

If it does not work locally, it will not work on the HPC cluster - frequent failures will lead to temporary account suspensions.

### Recommended Mindset

Design Docker images as if they were command-line programs.

A user should be able to run:

```bash
docker run my-image
```

and have the entire workload execute automatically without any additional interaction.

If this works correctly, the image is usually well suited for HPC execution.

## Minimal Docker Example

Create a directory:

```bash
mkdir count_to_60
cd count_to_60
```

Create `main.py`:

```python
import pathlib
import time

output_dir = pathlib.Path("/workspace/output")
output_dir.mkdir(parents=True, exist_ok=True)

for i in range(60):
    print(f"Count: {i}")
    time.sleep(1)

(output_dir / "result.txt").write_text(
    "Job completed successfully\n",
    encoding="utf-8",
)

print("Finished")
```

Create `Dockerfile`:

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

### Logging

Anything written to standard output is captured by the scheduler.

Example:

```python
print("Training started")
print("Epoch 1")
print("Epoch 2")
```

These messages can be viewed later using:

```bash
hpc-client logs <job_id>
```

### Writing Outputs

Save outputs into:

```text
/workspace/output
```

Example:

```python
from pathlib import Path

output_dir = Path("/workspace/output")
output_dir.mkdir(parents=True, exist_ok=True)

(output_dir / "metrics.csv").write_text(
    "episode,reward\n1,123\n",
    encoding="utf-8",
)
```

### Accessing Outputs

When a job completes, everything written to:

```text
/workspace/output
```

is copied back to the HPC storage.

Outputs are available through:

* The HPC Client
* The shared NAS outputs directory

The scheduler preserves the directory structure created inside:

```text
/workspace/output
```

For example:

```python
from pathlib import Path

output_dir = Path("/workspace/output")

(output_dir / "results").mkdir(exist_ok=True)

(output_dir / "results" / "metrics.csv").write_text(
    "episode,reward\n1,123\n",
    encoding="utf-8",
)
```

will produce:

```text
results/
└── metrics.csv
```

in the final job outputs.

### Viewing Logs

Anything written to standard output is automatically captured by the scheduler.

Example:

```python
print("Training started")
print("Epoch 1")
print("Epoch 2")
```

View logs using:

```bash
hpc-client logs <job_id>
```

### Logs vs Outputs

Logs and outputs serve different purposes.

| Type    | Purpose                                                             |
| ------- | ------------------------------------------------------------------- |
| Logs    | Progress updates, debugging information, training status            |
| Outputs | Models, checkpoints, CSV files, images, reports, evaluation results |

Example:

```python
print("Training complete")
```

appears in the logs.

```python
(output_dir / "model.pt").write_bytes(...)
```

appears in the job outputs.

### Recommended Output Structure

For larger projects, organise outputs into folders:

```text
/workspace/output
├── checkpoints
├── figures
├── logs
├── models
└── results
```

This structure will be preserved when the job finishes.

### Important

!!! warning "Outputs Must Be Saved Explicitly"
    Files written anywhere outside:

    ```text
    /workspace/output
    ```

    are temporary and may be lost when the container exits.

    Always save final outputs, checkpoints and results into:

    ```text
    /workspace/output
    ```


### Using Datasets

Requested datasets appear automatically inside the container.

Example:

```python
from pathlib import Path

dataset_root = Path("/workspace/datasets/mnist")

for file in dataset_root.iterdir():
    print(file)
```

Datasets are mounted read-only.

Do not attempt to modify dataset contents.

## Docker Images

Jobs can run images from either:

* Images pushed to the HPC registry
* Public images available from Docker Hub

!!! info "Registry Images and Docker Hub Images"

    HPC registry example:

    ```json
    {
      "image": "130.216.238.2:5500/count-to-60:latest"
    }
    ```

    Docker Hub example:

    ```json
    {
      "image": "python:3.11-slim"
    }
    ```

### Using Docker Hub

Public images hosted on Docker Hub can be used directly.

Examples:

```json
{
  "image": "python:3.11-slim"
}
```

```json
{
  "image": "pytorch/pytorch:latest"
}
```

If no registry address is specified, Docker will attempt to pull the image from Docker Hub.

### CARES HPC Registry

The CARES HPC Registry is hosted on the CARES NAS.

Registry address:

```text
130.216.238.2:5500
```

```json
{
  "image": "130.216.238.2:5500/count-to-60:latest"
}
```

The CARES HPC Registry is recommended for:

* Custom research code
* Private project images
* Shared laboratory images
* Images not published on Docker Hub
* Unlimited storage of Docker images

#### Trusting the CARES Docker Registry

The CARES registry is hosted locally and may be configured as an insecure registry.

Docker must be configured to trust the registry before images can be pushed or pulled.

Registry:

```text
130.216.238.2:5500
```

**Linux**

Edit:

```text
/etc/docker/daemon.json
```

Example:

```json
{
  "insecure-registries": [
    "130.216.238.2:5500"
  ]
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

Verify:

```bash
docker pull 130.216.238.2:5500/test-image:latest
```

**Docker Desktop**

Open:

```text
Settings
→ Docker Engine
```

Add:

```json
{
  "insecure-registries": [
    "130.216.238.2:5500"
  ]
}
```

Apply and restart Docker.

##### Verify Configuration

The following command should no longer produce certificate or trust errors:

```bash
docker pull 130.216.238.2:5500/count-to-60:latest
```

!!! warning "One-Time Configuration"

    This only needs to be configured once per machine.

    After the registry has been added to Docker's trusted registry list, images can be pushed and pulled normally.

#### Pushing an HPC Registry Image

Tag the image for the registry:

```bash
docker tag \
    count-to-60:latest \
    130.216.238.2:5500/count-to-60:latest
```

Verify:

```bash
docker images
```

Push the image:

```bash
docker push \
    130.216.238.2:5500/count-to-60:latest
```

Verify:

```bash
docker pull \
    130.216.238.2:5500/count-to-60:latest
```

If the image pulls successfully, it is ready to use in a job submission.

#### Updating an HPC Registry Image

After making code changes:

```bash
docker build -t count-to-60:latest .

docker tag \
    count-to-60:latest \
    130.216.238.2:5500/count-to-60:latest

docker push \
    130.216.238.2:5500/count-to-60:latest
```

The next submitted job will use the updated image.

## Common Mistakes

??? failure "Outputs Missing"

    Files were written somewhere other than:

    ```text
    /workspace/output
    ```

??? failure "Dataset Not Found"

    The dataset was not requested in `job.json`.

    The dataset path was not read from the correct path in the container:

    ```text
    /workspace/datasets/<dataset_name>
    ```


??? failure "Module Not Found"
    The required package was not installed inside the Docker image.

    Rebuild and push the image after updating the Dockerfile.

??? failure "Old Code Is Running"
    The updated image was not pushed to the registry.

    Rebuild, tag and push the image again.

## Next Steps

Continue with:

* Jobs
* Datasets
* Outputs
