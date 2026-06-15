# HPC Client

Student command-line and Python client for submitting jobs to the HPC Scheduler.

This package lets you submit jobs, check their status, view logs, wait for completion, and cancel jobs without needing access to the scheduler source code or scheduler machine.

## Install

From the `hpc-client` repository:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e .
```

Check the command is available:

```bash
hpc-client --help
```
### Allow Insecure Docker Registry Access

The CARES Docker registry is served over HTTP rather than HTTPS.

Each machine that needs to push or pull images must explicitly allow the registry as an insecure registry.

Edit Docker daemon configuration:

```bash
sudo nano /etc/docker/daemon.json
```

You should already see the Nvidia runtime configured - add the insecure registry configuration:

```json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "insecure-registries": [
    "130.216.238.2:5500"
  ]
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

Verify Docker sees the insecure registry configuration:

```bash
docker info | grep -A5 "Insecure Registries"
```

Expected output should include:

```text
130.216.238.2:5500
```

## Configure

Point the client at the scheduler:

```bash
hpc-client configure --scheduler-url http://localhost:8080
```

For the real scheduler, use the URL provided by the HPC admin.

## Login

Use your UPI and password:

```bash
hpc-client login <your-upi>
```

Example:

```bash
hpc-client login test123
```

Check your login:

```bash
hpc-client whoami
```

## Job file

Jobs are submitted as JSON files.

Example `job.json`:

```json
{
  "job_name": "long_dataset_test",
  "image": "130.216.238.2:5500/hpc-test:latest",
  "max_runtime_hours": 1.0,
  "command": null,
  "required_datasets": [],
  "required_worker_ids": []
}
```

Fields:

| Field | Description |
|---|---|
| `job_name` | Human-readable job name |
| `image` | Docker image to run |
| `max_runtime_hours` | Maximum allowed runtime |
| `command` | Optional command override, or `null` to use the image default |
| `required_datasets` | Dataset names required by the job |
| `required_worker_ids` | Optional worker restriction; usually leave empty |

## Building and Publishing Docker Images

Jobs are executed using Docker images.

Students build their application into a Docker image, push the image to the CARES registry, and then reference that image in their `job.json`.

---

### Example Project

```text
my_project/
├── Dockerfile
├── requirements.txt
├── train.py
└── job.json
```

---

### Example Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "train.py"]
```

---

### Example Training Script

```python
from pathlib import Path

output_dir = Path("/workspace/output")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "results.txt", "w") as f:
    f.write("Training complete\n")

print("Done")
```

Anything written to:

```text
/workspace/output
```

will automatically be copied back to the scheduler output directory.

---

### Build the Image

From the project directory:

```bash
docker build -t my-training-image:latest .
```

Verify:

```bash
docker images
```

---

### Tag for the CARES Registry

Assuming the registry is:

```text
130.216.238.2:5500
```

tag the image:

```bash
docker tag \
    my-training-image:latest \
    130.216.238.2:5500/my-training-image:latest
```

---

### Push to the Registry

```bash
docker push \
    130.216.238.2:5500/my-training-image:latest
```

Verify the push completed successfully.

---

### Reference the Image in job.json

```json
{
  "job_name": "training_run",
  "image": "130.216.238.2:5500/my-training-image:latest",
  "max_runtime_hours": 4.0,
  "command": null,
  "required_datasets": [],
  "required_worker_ids": []
}
```

Submit:

```bash
hpc-client submit job.json
```

---

### Overriding the Docker Command

If the Docker image contains multiple entry points, you can override the command at submission time.

Example:

```json
{
  "job_name": "seed_1",
  "image": "130.216.238.2:5500/my-training-image:latest",
  "max_runtime_hours": 4.0,
  "command": "python train.py --seed 1",
  "required_datasets": [],
  "required_worker_ids": []
}
```

The scheduler will execute:

```bash
python train.py --seed 1
```

inside the container instead of the Dockerfile `CMD`.

---

### Datasets

Datasets requested in:

```json
{
  "required_datasets": [
    "imagenet"
  ]
}
```

are mounted inside the container at:

```text
/workspace/datasets/imagenet
```

Datasets are mounted read-only.

Do not modify dataset contents.

---

### Output Files

Job outputs should be written to:

```text
/workspace/output
```

Examples:

```python
"/workspace/output/results.csv"
"/workspace/output/checkpoint.pt"
"/workspace/output/model.pth"
"/workspace/output/log.txt"
```

Files written here are automatically copied to the scheduler output directory when the job completes.

---

### Important: Containers Are Temporary

Docker containers are not persistent.

Anything written outside:

```text
/workspace/output
```

will be lost when the job finishes.

For example:

```text
/workspace/output/model.pt      ✅ Saved
/workspace/output/results.csv   ✅ Saved

/tmp/model.pt                   ❌ Lost
/workspace/model.pt             ❌ Lost
```

Always save checkpoints, models, logs, and results into:

```text
/workspace/output
```

Your code needs to handle passing data to the output directory and ensuring important files are saved there. No output written outside this directory will be preserved after the job finishes.

## Submit a job

```bash
hpc-client submit job.json
```

The output includes a `job_id`. Save this for logs/status/cancel operations.

## List jobs

```bash
hpc-client jobs
```

For raw JSON:

```bash
hpc-client jobs --json
```

## Show one job

```bash
hpc-client job <job_id>
```

## Wait for a job to finish

```bash
hpc-client wait <job_id>
```

Custom polling interval:

```bash
hpc-client wait <job_id> --poll-seconds 5
```

## View logs

```bash
hpc-client logs <job_id>
```

For raw JSON:

```bash
hpc-client logs <job_id> --json
```

## Cancel a job

```bash
hpc-client cancel <job_id>
```

## Typical workflow

```bash
hpc-client configure --scheduler-url http://localhost:8080
hpc-client login <your-upi>

hpc-client submit job.json
hpc-client jobs
hpc-client wait <job_id>
hpc-client logs <job_id>
```

## Python usage

You can also submit jobs from Python scripts.

```python
from hpc_client import HPCClient

client = HPCClient.from_config()

result = client.submit("job.json")
job_id = result["job_id"]

print("Submitted:", job_id)

finished = client.wait(job_id, poll_seconds=5)
print(finished)

logs = client.logs(job_id)
print(logs.get("container_log"))
```

Example parameter sweep:

```python
from hpc_client import HPCClient

client = HPCClient.from_config()

image = "130.216.238.2:5500/my-training-image:latest"

for seed in range(5):
    result = client.submit(
        {
            "job_name": f"training_seed_{seed}",
            "image": image,
            "command": f"python train.py --seed {seed}",
            "max_runtime_hours": 4.0,
            "required_datasets": [],
            "required_worker_ids": [],
        }
    )

    print("Submitted:", result["job_id"])
```

## Configuration location

The client stores configuration locally at:

```text
~/.hpc/config.json
```

This stores the scheduler URL and login session cookie.

If login stops working, run:

```bash
hpc-client login <your-upi>
```

again.

## Troubleshooting

### `Not logged in`

Run:

```bash
hpc-client login <your-upi>
```

### `Could not connect`

Check that the scheduler URL is correct:

```bash
hpc-client configure --scheduler-url <scheduler-url>
```

### Job stays queued

There may be no available workers, or your job may be waiting behind other jobs.

Check:

```bash
hpc-client jobs
```

### Logs are empty

The job may not have started yet, or output may not have synced yet.

Try:

```bash
hpc-client wait <job_id>
hpc-client logs <job_id>
```

## Notes

Students do not need access to the scheduler machine or scheduler source code.

All interaction happens through the scheduler API using this client.