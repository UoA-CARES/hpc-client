# Installation

## Requirements

Before installing the HPC Client you must:

- Have an HPC account created by the administrators
- Have network access to the scheduler
- Have Python 3.10 or newer installed

!!! warning "Account Required"

    Students and researchers cannot create accounts through the client.

    Contact the HPC administrators and request an account before continuing.

    Provide:

    - UPI
    - University email address
    - Supervisor
    - Intended HPC usage

## Install HPC Client

Clone the repository:

```bash
git clone git@github.com:UoA-CARES/hpc-client.git
cd hpc-client
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install:

```bash
pip install -e .
```

Verify:

```bash
hpc-client --help
```

## Configure Scheduler

Configure the scheduler URL:

```bash
hpc-client configure \
    --scheduler-url http://scheduler.example.nz:8080
```

Verify:

```bash
hpc-client config
```

Example output:

```text
Scheduler URL: http://scheduler.example.nz:8080
```

## Login

Login using your HPC account:

```bash
hpc-client login <upi>
```

Example:

```bash
hpc-client login abc123
```

You will be prompted for your password.

Successful login stores a session token locally.

## Verify Access

Display current user information:

```bash
hpc-client whoami
```

Example:

```text
Username: abc123
Role: postgraduate
Email: abc123@aucklanduni.ac.nz
```

List jobs:

```bash
hpc-client jobs
```

A successful response confirms communication with the scheduler.

## Upgrade

Update the repository:

```bash
git pull
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Reinstall:

```bash
pip install -e .
```

## Logout

Remove the stored session:

```bash
hpc-client logout
```

You will need to login again before submitting jobs.

## Next Steps

Continue with:

- Docker Images
- Jobs
- Datasets
- Outputs