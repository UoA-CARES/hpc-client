import argparse
import getpass
import json
import sys
from typing import Any

from hpc_client.client import HPCClient
from hpc_client.config import HPCConfig
from hpc_client.errors import HPCClientError


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2))


def command_configure(args: argparse.Namespace) -> None:
    config = HPCConfig(
        scheduler_url=args.scheduler_url.rstrip("/"),
    )
    config.save()

    print_json(
        {
            "ok": True,
            "scheduler_url": config.scheduler_url,
            "config_path": (
                str(args.config_path) if hasattr(args, "config_path") else None
            ),
        }
    )


def command_login(args: argparse.Namespace) -> None:
    config = HPCConfig.load()

    password = args.password
    if password is None:
        password = getpass.getpass("Password: ")

    client = HPCClient(config.scheduler_url)
    data = client.login(
        username=args.username,
        password=password,
        save=True,
    )

    print_json(data)


def command_logout(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    data = client.logout()
    print_json(data)


def command_whoami(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    print_json(client.me())


def command_submit(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    data = client.submit(args.job_file)

    print_json(data)


def command_jobs(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    jobs = client.jobs()

    if args.json:
        print_json(jobs)
        return

    print_jobs_table(jobs)


def command_job(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    print_json(client.job(args.job_id))


def command_logs(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    data = client.logs(args.job_id)

    if args.json:
        print_json(data)
        return

    container_log = data.get("container_log")
    result_text = data.get("result_text")
    rsync_output_log = data.get("rsync_output_log")

    if container_log:
        print("===== container.log =====")
        print(container_log)

    if result_text:
        print("===== result.txt =====")
        print(result_text)

    if rsync_output_log:
        print("===== rsync_output.log =====")
        print(rsync_output_log)


def command_cancel(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    print_json(client.cancel(args.job_id))


def command_wait(args: argparse.Namespace) -> None:
    client = HPCClient.from_config()
    data = client.wait(
        job_id=args.job_id,
        poll_seconds=args.poll_seconds,
    )
    print_json(data)


def print_jobs_table(jobs: list[dict[str, Any]]) -> None:
    rows = []

    for item in jobs:
        rows.append(
            {
                "Job ID": item.get("job_id", ""),
                "Name": item.get("job_name", ""),
                "Status": item.get("status", ""),
                "Tier": item.get("tier_name", ""),
                "Worker": item.get("assigned_worker_id", ""),
                "Submitted": item.get("submitted_at", ""),
            }
        )

    if not rows:
        print("No jobs.")
        return

    columns = ["Job ID", "Name", "Status", "Tier", "Worker", "Submitted"]

    widths = {
        column: max(
            len(column),
            *(len(str(row[column])) for row in rows),
        )
        for column in columns
    }

    print("  ".join(column.ljust(widths[column]) for column in columns))
    print("  ".join("-" * widths[column] for column in columns))

    for row in rows:
        print("  ".join(str(row[column]).ljust(widths[column]) for column in columns))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Student CLI for the HPC Scheduler.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    configure = subparsers.add_parser("configure")
    configure.add_argument("--scheduler-url", required=True)
    configure.set_defaults(func=command_configure)

    login = subparsers.add_parser("login")
    login.add_argument("username")
    login.add_argument("--password")
    login.set_defaults(func=command_login)

    logout = subparsers.add_parser("logout")
    logout.set_defaults(func=command_logout)

    whoami = subparsers.add_parser("whoami")
    whoami.set_defaults(func=command_whoami)

    submit = subparsers.add_parser("submit")
    submit.add_argument("job_file")
    submit.set_defaults(func=command_submit)

    jobs = subparsers.add_parser("jobs")
    jobs.add_argument("--json", action="store_true")
    jobs.set_defaults(func=command_jobs)

    job = subparsers.add_parser("job")
    job.add_argument("job_id")
    job.set_defaults(func=command_job)

    logs = subparsers.add_parser("logs")
    logs.add_argument("job_id")
    logs.add_argument("--json", action="store_true")
    logs.set_defaults(func=command_logs)

    cancel = subparsers.add_parser("cancel")
    cancel.add_argument("job_id")
    cancel.set_defaults(func=command_cancel)

    wait = subparsers.add_parser("wait")
    wait.add_argument("job_id")
    wait.add_argument("--poll-seconds", type=float, default=10.0)
    wait.set_defaults(func=command_wait)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except HPCClientError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
