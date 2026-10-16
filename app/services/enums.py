from enum import Enum


class RunStatus(str, Enum):
    RUNNING = "running"
    EXPORTED = "exported"
    COMPLETED = "completed"
    FAILED = "failed"