from enum import StrEnum, auto, unique

@unique
class Concurrency(StrEnum):
    """Concurrency type for the callable. See https://docs.python.org/3/library/asyncio.html"""
    Sync = auto()
    Async = auto()

