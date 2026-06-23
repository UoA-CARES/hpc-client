# Job Priorities and Scheduling Tiers

The HPC Scheduler uses scheduling tiers to ensure fair access to shared computing resources while still allowing machines to remain highly utilised. Every submitted job is automatically assigned a scheduling tier based on the number of jobs you currently have running and your user policy - this tiering is dynamic and is updated as jobs complete and workers become available. Jobs in higher-priority tiers are scheduled before jobs in lower-priority tiers when resources become available. This system allows users to run multiple experiments in parallel while ensuring that no single user can monopolise the cluster. All jobs are otherwise treated equally within their assigned tier, with jobs being executed in the order they were submitted.

!!! note "Tiers Summary"
    Scheduling priority is applied in the following order:

    1. Normal - Jobs within your normal allocation
    2. Overflow - Jobs that exceed your normal allocation but are still within your overflow limit
    3. Opportunistic - Jobs that exceed both your normal and overflow limits and only run when spare capacity is available and can be `preempted` by higher-priority jobs.

    The scheduler automatically manages these tiers based on your current usage and user policy, so no manual action is required when submitting jobs.

The scheduling tiers are as follows:

## Normal

Normal jobs are your standard allocation of cluster resources. As long as you have not exceeded your normal running job limit, newly submitted jobs will be placed in the **Normal** tier. These jobs receive priority over Overflow and Opportunistic jobs.

## Overflow

Overflow jobs allow users to temporarily exceed their normal allocation when spare capacity is available. Once you reach your Normal job limit, additional jobs may enter the **Overflow** tier. Overflow jobs are scheduled after all Normal jobs but before Opportunistic jobs. This provides flexibility for larger experiment batches while still ensuring fair access for other users.

!!! note "Postgraduate and Staff users only"
    Undergraduate users do not have access to the Overflow tier and will have their jobs placed in the Opportunistic tier once they exceed their Normal job limit.

## Opportunistic

Opportunistic jobs are used when a user has already consumed both their Normal and Overflow allocations. These jobs only run when cluster resources would otherwise be idle. Opportunistic jobs have the lowest scheduling priority and may wait longer before being assigned to a worker. This tier allows users to continue submitting work without preventing higher-priority jobs from running. 

These jobs will only run when there are no Normal or Overflow jobs waiting and there is spare capacity on the cluster. This allows users to make use of idle resources while ensuring that higher-priority work is not delayed.

!!! warning "Opportunistic jobs may be cancelled"
    Opportunistic jobs may be `preempted` if a higher-priority job is submitted while they are running and no other workers are available. This means that if you have an opportunistic job running and someone submits a normal or overflow job, the opportunistic job will be stopped and moved back to the queue until resources become available again.

## Blocked

The **Blocked** tier is reserved for administrative and future scheduling features and is not currently used during normal operation. Jobs assigned to the Blocked tier are excluded from scheduling until their status is changed by the scheduler or an administrator.

## How Jobs Move Between Tiers

The scheduler automatically determines a job's tier based on the number of jobs you currently have running.

For example, a Postgraduate user receives:

* The first 5 running jobs in the **Normal** tier.
* The next 2 running jobs in the **Overflow** tier.
* Any additional jobs in the **Opportunistic** tier.

As jobs complete, queued jobs automatically move into higher-priority tiers again. For instance, if a Normal job finishes and you have an Overflow job waiting, that Overflow job will be promoted to Normal and scheduled accordingly. 

## User Role Allocations

Each user role has a default allocation that determines how many jobs can run in each scheduling tier.

| User Role     | Normal Jobs | Overflow Jobs | Opportunistic Jobs |
| ------------- | ----------- | ------------- | ------------------ |
| Undergraduate | 3           | 0             | Unlimited*         |
| Postgraduate  | 5           | 2             | Unlimited*         |
| Staff         | 5           | 2             | Unlimited*         |
| Administrator | Unlimited   | Unlimited     | Unlimited          |

* Opportunistic jobs are run when a user is beyond the Normal and Overflow limits but will only run when spare cluster capacity is available and all higher-priority work has been allocated.
