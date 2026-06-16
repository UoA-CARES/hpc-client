# Datasets

Datasets allow jobs to access shared data stored on the HPC system.

Datasets are stored on the CARES NAS and mounted automatically to a given worker then into containers when requested by a job.

## Dataset Storage

Datasets are stored on the shared CARES NAS under the `datasets` folder:

```text
/cares-nas/datasets/<dataset_name>
```

Each user is responsible for:

- Uploading their own datasets
- Organising their dataset folders
- Updating dataset contents
- Removing unused datasets

The HPC administrators maintain the infrastructure but do not manage individual research datasets.

Contact the HPC administrators only if:

- You need access to the NAS
- You require additional storage
- You encounter permissions issues
- A dataset is unavailable due to a system issue
- Private Data that can't be stored on the public NAS

!!! warning "Dataset Permissions"
    Please avoid modifying datasets belonging to other users or projects.

    Do not delete or modify datasets that you do not own.

    Datasets are shared resources and should be treated with care.

!!! info "Private or Sensitive Data"
    If you have sensitive data that cannot be shared, do not upload it to the CARES NAS.

    Speak with the HPC administrators about alternative storage options.

## Creating a Dataset

Datasets are stored on the CARES NAS: `http://130.216.238.2:5000/`

The recommended approach is to mount the datasets share directly on your computer.

Once mounted, datasets can be copied using:

- Drag and drop
- File Explorer
- Finder
- cp
- rsync

This is significantly more reliable than browser uploads for large datasets.

### Linux

Create a mount point:

```bash
sudo mkdir -p /mnt/cares_datasets
```

Mount:

```bash
sudo mount -t cifs \
    //130.216.238.2/datasets \
    /mnt/cares_datasets \
    -o username=<username>
```

Verify:

```bash
ls /mnt/cares_datasets
```

### Windows

Open:

```text
\\130.216.238.2\datasets
```

in File Explorer.

Or map a network drive:

```text
This PC
→ Map Network Drive
→ \\130.216.238.2\datasets
```

### macOS

In Finder:

```text
Go
→ Connect to Server
```

Enter:

```text
smb://130.216.238.2/datasets
```

Authenticate using your HPC credentials.

### Uploading a Dataset

Create a dataset directory:

```text
datasets/
└── project_xyz
```

Copy files into that directory.

Example:

```text
datasets/
└── project_xyz
    ├── train
    ├── test
    └── metadata.csv
```

The directory name becomes the dataset name.

Example:

```json
{
  "required_datasets": ["project_xyz"]
}
```

Inside the container:

```text
/workspace/datasets/project_xyz
```

#### Large Dataset Transfers

For large datasets, use rsync.

Example:

```bash
rsync -avh \
    ./project_xyz/ \
    /mnt/cares_datasets/project_xyz/
```

Advantages:

- Resumes interrupted transfers
- Transfers only changed files
- Faster updates for large datasets

## Using a Dataset

Datasets are requested by a job through the:

```json
"required_datasets"
```

field in `job.json`.

Example:

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

## Dataset Names

Datasets are referenced by the name of the folder on the CARES NAS dataset folder.

```text
/nas/datasets/<dataset_name>
```

Example:

```json
"required_datasets": [
    "mnist",
    "cifar10",
    "imagenet"
]
```

The scheduler automatically mounts the corresponding dataset directories into the container.

!!! warning "Name Mismatch"

    If the dataset name in `job.json` does not exactly match a dataset folder name on the CARES NAS, the job will fail before execution begins.

## Accessing Datasets

Datasets appear inside the container at:

```text
/workspace/datasets/<dataset_name>
```

Examples:

```text
/workspace/datasets/mnist
/workspace/datasets/cifar10
/workspace/datasets/imagenet
```

Python example:

```python
from pathlib import Path

dataset_root = Path("/workspace/datasets/mnist")

for file in dataset_root.iterdir():
    print(file)
```

!!! info "File Structure"

    The internal structure of a dataset is preserved when mounted into the container.

    For example, if the dataset on the CARES NAS has the structure:

    ```text
    mnist/
    ├── train
    ├── test
    └── labels.csv
    ```

    then inside the container it will appear as:

    ```text
    /workspace/datasets/mnist
    ├── train
    ├── test
    └── labels.csv
    ```

!!! warning "Responsibility to Save Outputs"

    Datasets are read-only.

    Your code needs to handle passing data to the output directory and ensuring important files are saved there. No output written outside this directory will be preserved after the job finishes.

    Always save final outputs, checkpoints and results into:

    ```text
    /workspace/output
    ```

    ```python
    from pathlib import Path

    dataset_root = Path("/workspace/datasets/mnist")
    output_root = Path("/workspace/output")

    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Reading data from: {dataset_root}")
    print(f"Writing results to: {output_root}")
    ```

!!! warning "Read-Only Access"

    Datasets are mounted read-only.

    Do not attempt to modify dataset contents.

## Multiple Datasets

Multiple datasets can be requested.

Example:

```json
{
  "required_datasets": [
    "mnist",
    "cifar10"
  ]
}
```

Inside the container:

```text
/workspace/datasets/mnist
/workspace/datasets/cifar10
```

## Read-Only Access

Datasets are mounted read-only.

You should treat datasets as immutable.

Do not:

- modify files
- rename files
- delete files
- create files inside dataset directories

Instead write outputs to:

```text
/workspace/output
```

## Dataset Availability

Only datasets that have been uploaded to the CARES NAS can be used.

If a requested dataset does not exist, the job will fail before execution begins.

Example:

```json
"required_datasets": ["my_typo_dataset"]
```

If the dataset is unavailable, contact the HPC administrators.


## Common Mistakes

??? failure "Dataset Not Found"

    Check the dataset name in:

    ```json
    "required_datasets": ["dataset_name"]
    ```

    Dataset names must exactly match the registered dataset name.

??? failure "Permission Denied"

    Datasets are mounted read-only.

    Save outputs into:

    ```text
    /workspace/output
    ```

??? failure "Files Missing"

    Verify the dataset structure using:

    ```python
    from pathlib import Path

    dataset_root = Path("/workspace/datasets/mnist")

    for file in dataset_root.rglob("*"):
        print(file)
    ```

    to inspect the mounted dataset contents.