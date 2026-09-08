# Job Priorities and Scheduling Tiers

The HPC Scheduler uses scheduling tiers to ensure fair access to shared computing resources while still allowing machines to remain highly utilised.

Every submitted job is automatically assigned a scheduling tier based on the number of jobs you currently have running, your user policy, the requested maximum runtime, and whether the job is resumable. Tiering is dynamic and is updated as jobs complete and capacity becomes available.

Jobs in higher-priority tiers are scheduled before jobs in lower-priority tiers when resources become available. This allows users to run multiple experiments in parallel without allowing a single user to monopolise the cluster.

Within the same tier, jobs are generally scheduled in the order they were submitted.

!!! note "Tiers Summary"
    Scheduling priority is applied in the following order:

    1. **Normal** - Jobs within your normal allocation.
    2. **Overflow** - Jobs above your normal allocation but within your overflow allowance.
    3. **Opportunistic** - Jobs using spare cluster capacity. Some opportunistic jobs may become preemptible.
    4. **Held** - Long, non-resumable jobs that are outside your current Normal and Overflow allocation.

    The scheduler automatically manages these tiers as your current usage changes.

## Normal

Normal jobs are your standard allocation of cluster resources.

As long as you have not exceeded your normal running-job limit, jobs are placed in the **Normal** tier. These jobs receive priority over Overflow and Opportunistic jobs.

## Overflow

Overflow jobs allow users to temporarily exceed their normal allocation.

Once you reach your Normal job limit, additional jobs may enter the **Overflow** tier. Overflow jobs are scheduled after Normal jobs but before Opportunistic jobs.

This provides flexibility for larger experiment batches while still ensuring fair access for other users.

!!! note "Postgraduate and Staff users only"
    Undergraduate users do not have an Overflow allocation and will move directly from Normal into Opportunistic or Held scheduling once their Normal allocation is consumed.

## Opportunistic

Opportunistic jobs allow otherwise idle workers to be used when a user has already consumed their Normal and Overflow allocations.

These jobs have the lowest active scheduling priority and only run when spare compatible worker capacity is available.

Whether a job can run opportunistically depends on its requested maximum runtime and whether it is resumable.

### Jobs requesting 24 hours or less

Jobs with:

```text
max_runtime_hours <= 24
```

may run as **Opportunistic** jobs even if they are not resumable.

These short opportunistic jobs are **protected from automatic preemption**.

Once started, the scheduler will allow them to run normally rather than automatically stopping them to reclaim capacity.

### Jobs requesting more than 24 hours

Jobs with:

```text
max_runtime_hours > 24
```

must be resumable to run opportunistically.

A long resumable opportunistic job receives a **24-hour protected execution period** whenever it begins an execution stint.

During those first 24 hours, it will not be automatically preempted.

After 24 hours of uninterrupted execution, it becomes **Preemptible**.

If higher-priority work is waiting and there is no compatible idle worker available, the scheduler may then preempt the job and reclaim that worker.

!!! note "Protection is per execution stint"
    If a long resumable opportunistic job is preempted and later scheduled again, it receives a new 24-hour protected execution period before becoming automatically preemptible again.

### Preemption

Automatic preemption is deliberately conservative.

The scheduler only considers preemption when:

* a higher-priority Admin, Normal, or Overflow job is waiting;
* there is no compatible idle worker available for that job; and
* an eligible Opportunistic job has passed its protection period.

Only **one automatic preemption is requested at a time**. The scheduler then waits for the cluster state to settle before deciding whether another preemption is necessary.

This avoids stopping multiple jobs unnecessarily.

The job interface shows whether a running Opportunistic job is currently:

* **Protected** - it will not be automatically preempted;
* **Preemptible** - it may be stopped if higher-priority work requires its worker; or
* **Auto-preemption Off** - opportunistic preemption is currently disabled by the cluster administrator.

## Resumable Jobs and Preemption

The `resumable` option allows a job to continue from previously saved state after an interruption.

For scheduler-controlled preemption of a resumable job, the worker first stops the running container and persists the job's output state to NAS.

Only after that state has been successfully persisted is the job reported to the scheduler as preempted and moved back into the queue.

When the job is later scheduled again:

* surviving local job state is used when available;
* otherwise, previously saved output state is restored from NAS;
* if no previous resume state exists, the job starts normally.

This allows resumable opportunistic jobs to move between workers rather than depending on the original machine still being available.

!!! important "Your application must support checkpointing"
    Setting:

    ```yaml
    resumable: true
    ```

    does not automatically make your training code resumable.

    Your application should periodically save the state required to continue training into:

    ```text
    /workspace/output
    ```

    and check for an existing checkpoint when it starts.

    For example, a training script might:

    ```python
    if checkpoint_exists():
        load_checkpoint()
    else:
        start_from_scratch()
    ```

    The scheduler is responsible for preserving and restoring the output workspace. Your application is responsible for saving and loading a useful checkpoint within that workspace.

## Held

The **Held** tier is used for jobs that cannot safely use opportunistic scheduling.

A job will be Held when all of the following are true:

* the user's Normal allocation is already consumed;
* the user's Overflow allocation is already consumed;
* the job requests more than 24 hours of runtime; and
* the job is not resumable.

For example:

```text
max_runtime_hours = 48
resumable = false
```

cannot safely be started as Opportunistic work because the scheduler could not later reclaim the worker without discarding substantial progress.

The job is therefore placed in the **Held** tier until capacity becomes available within the user's Normal or Overflow allocation.

Held does not mean that the job has failed or been rejected. It is simply waiting for an allocation in which it can run safely.

## How Jobs Move Between Tiers

Scheduling tiers are dynamic.

For example, a Postgraduate user may have:

* the first 5 active jobs in **Normal**;
* the next 2 active jobs in **Overflow**;
* additional eligible jobs in **Opportunistic**;
* long non-resumable jobs beyond those allocations in **Held**.

As jobs complete, remaining jobs are automatically reconsidered.

For example, if a Normal job finishes, an Overflow or Opportunistic job may be promoted into Normal capacity.

Likewise, a Held job may move into Normal or Overflow once sufficient user allocation becomes available.

A running Opportunistic job can also be promoted into a higher tier if the user's allocation becomes available. Once it is no longer Opportunistic, it is no longer eligible for automatic opportunistic preemption.

## Examples

| Job                                           | Outside Normal/Overflow allocation | Result                                      |
| --------------------------------------------- | ---------------------------------- | ------------------------------------------- |
| 6-hour, non-resumable job                     | Yes                                | Opportunistic, protected                    |
| 24-hour, non-resumable job                    | Yes                                | Opportunistic, protected                    |
| 48-hour, non-resumable job                    | Yes                                | Held                                        |
| 48-hour, resumable job                        | Yes                                | Opportunistic, protected for first 24 hours |
| 48-hour, resumable job after 24 hours running | Yes                                | Opportunistic and preemptible               |
| Any job with Normal allocation available      | No                                 | Normal                                      |
| Any job with Overflow allocation available    | No                                 | Overflow                                    |

## User Role Allocations

Each user role has a default allocation that determines how many jobs can run in each scheduling tier.

| User Role     | Normal Jobs | Overflow Jobs | Opportunistic Jobs |
| ------------- | ----------: | ------------: | -----------------: |
| Undergraduate |           3 |             0 |          Unlimited |
| Postgraduate  |           5 |             2 |          Unlimited |
| Staff         |           5 |             2 |          Unlimited |
| Administrator |   Unlimited |     Unlimited |          Unlimited |

The exact allocation for an individual user may be adjusted by an administrator.
