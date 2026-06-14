import json
import pathlib
from dataclasses import dataclass

CONFIG_DIR = pathlib.Path.home() / ".hpc"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class HPCConfig:
    scheduler_url: str
    session_cookie: str | None = None
    username: str | None = None

    @classmethod
    def load(cls, path: pathlib.Path = CONFIG_PATH) -> "HPCConfig":
        if not path.exists():
            raise RuntimeError(
                f"No HPC config found at {path}. Run: hpc configure --scheduler-url URL"
            )

        data = json.loads(path.read_text(encoding="utf-8"))

        return cls(
            scheduler_url=data["scheduler_url"],
            session_cookie=data.get("session_cookie"),
            username=data.get("username"),
        )

    def save(self, path: pathlib.Path = CONFIG_PATH) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(
                {
                    "scheduler_url": self.scheduler_url.rstrip("/"),
                    "session_cookie": self.session_cookie,
                    "username": self.username,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
