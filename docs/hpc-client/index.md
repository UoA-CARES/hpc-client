# HPC Client

The HPC Client is the command-line tool and python api students and researchers use to submit Docker jobs to the CARES HPC Scheduler through automation tools.

With `hpc-client`, you can:

- Log in to the scheduler
- Submit jobs
- List your jobs
- Wait for a job to finish
- View job logs
- Cancel jobs

!!! warning "Account Required"
    You cannot create your own account through the client.

    Before using the HPC Client, contact the HPC administrators and request an account.

    Provide:

    - Your UPI
    - Your University of Auckland email address
    - Your name
    - Your supervisor
    - A short description of the work you want to run

    After your account is created, the administrators will provide your login details.

## Basic cli Workflow

```bash
hpc-client configure --scheduler-url http://<SCHEDULER_IP>:8080
hpc-client login <upi>
hpc-client submit job.json
hpc-client jobs
hpc-client wait <job_id>
hpc-client logs <job_id>
```

!!! tip "Scheduler URL"

    The scheduler IP is provided by the HPC administrators: contact them if you don't have this information [cares-hpc-support](https://caresuoa.slack.com/archives/C0B0AJKMCPM). 

### Step 1: Configure the Client

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

### Step 2: Create a Job

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

### Step 3: Monitor the Job

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

## Automating Job submissions from Python

The client can also be used directly from Python to automate job submissions.

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

!!! warning "Maximum Job Limit"
    Each user can have a maximum of 50 jobs in the queue to prevent spam.

    If you submit more than 50 jobs, they will be rejected until some of your existing jobs complete or are cancelled.