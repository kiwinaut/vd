from enum import Enum

class Status(Enum):
    SLEEP = 0
    QUEUED = 1
    ACTIVE = 2
    SOLVING = 3
    DOWNLOAD = 4