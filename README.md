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