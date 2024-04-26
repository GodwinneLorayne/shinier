from enum import StrEnum, auto, unique
from pydantic import BaseModel

@unique
class Concurrency(StrEnum):
    """Concurrency type for the callable. See https://docs.python.org/3/library/asyncio.html"""
    Sync = auto()
    Async = auto()


class Callable(BaseModel):
    """A callable object"""
    name: str
    concurrency: Concurrency
