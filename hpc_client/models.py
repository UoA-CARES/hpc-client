from typing import Any

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    job_name: str
    image: str
    command: str | None

    max_runtime_hours: float = 1.0

    required_datasets: list[str] = Field(default_factory=list)
    required_worker_ids: list[str] = Field(default_factory=list)

    env: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
