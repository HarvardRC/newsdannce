from enum import Enum


class JobState(Enum):
    COMPLETED = "COMPLETED"
    COMPLETING = "COMPLETING"
    FAILED = "FAILED"
    PENDING = "PENDING"
    PREEMPTED = "PREEMPTED"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    STOPPED = "STOPPED"

    def is_alive(self):
        return self in [JobState.PENDING, JobState.COMPLETING, JobState.RUNNING]
