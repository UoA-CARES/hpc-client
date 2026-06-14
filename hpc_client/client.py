import json
import pathlib
import time
from typing import Any

import httpx

from hpc_client.config import HPCConfig
from hpc_client.errors import HPCAuthenticationError, HPCRequestError
from hpc_client.models import JobSpec

TERMINAL_STATUSES = {
    "completed",
    "failed",
    "cancelled",
    "deleted",
}


class HPCClient:
    def __init__(
        self,
        scheduler_url: str,
        session_cookie: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.scheduler_url = scheduler_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout)

        if session_cookie:
            self.client.cookies.set("hpc_session", session_cookie)

    @classmethod
    def from_config(cls) -> "HPCClient":
        config = HPCConfig.load()

        return cls(
            scheduler_url=config.scheduler_url,
            session_cookie=config.session_cookie,
        )

    def close(self) -> None:
        self.client.close()

    def _request(
        self,
        method: str,
        path: str,
        json_data: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.scheduler_url}{path}"

        response = self.client.request(
            method,
            url,
            json=json_data,
        )

        if response.status_code == 401:
            raise HPCAuthenticationError("Not logged in. Run: hpc login")

        try:
            data = response.json()
        except ValueError:
            data = response.text

        if response.status_code >= 400:
            raise HPCRequestError(f"{response.status_code}: {data}")

        return data

    def login(
        self,
        username: str,
        password: str,
        save: bool = True,
    ) -> dict[str, Any]:
        data = self._request(
            "POST",
            "/auth/login",
            {
                "username": username,
                "password": password,
            },
        )

        session_cookie = self.client.cookies.get("hpc_session")

        if save:
            config = HPCConfig(
                scheduler_url=self.scheduler_url,
                session_cookie=session_cookie,
                username=username,
            )
            config.save()

        return data

    def logout(self) -> dict[str, Any]:
        data = self._request("POST", "/auth/logout")

        config = HPCConfig.load()
        config.session_cookie = None
        config.save()

        return data

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/auth/me")

    def submit(
        self,
        job: JobSpec | dict[str, Any] | str | pathlib.Path,
    ) -> dict[str, Any]:
        if isinstance(job, JobSpec):
            payload = job.model_dump()
        elif isinstance(job, dict):
            payload = JobSpec(**job).model_dump()
        else:
            payload = self.load_job_file(pathlib.Path(job)).model_dump()

        return self._request(
            "POST",
            "/jobs",
            payload,
        )

    def jobs(self) -> list[dict[str, Any]]:
        return self._request("GET", "/jobs")

    def job(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/jobs/{job_id}")

    def logs(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/jobs/{job_id}/logs")

    def cancel(self, job_id: str) -> dict[str, Any]:
        return self._request("POST", f"/jobs/{job_id}/cancel")

    def wait(
        self,
        job_id: str,
        poll_seconds: float = 10.0,
    ) -> dict[str, Any]:
        while True:
            data = self.job(job_id)
            job = data.get("job", data)

            status = job.get("status")

            if status in TERMINAL_STATUSES:
                return data

            time.sleep(poll_seconds)

    @staticmethod
    def load_job_file(path: pathlib.Path) -> JobSpec:
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(f"Job file must contain a JSON object: {path}")

        return JobSpec(**data)
