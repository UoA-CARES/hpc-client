from typing import Any

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    job_name: str
    image: str
    command: str | None = None

    max_runtime_hours: float = 1.0

    resumable: bool = False

    required_datasets: list[str] = Field(default_factory=list)
    required_worker_ids: list[str] = Field(default_factory=list)
