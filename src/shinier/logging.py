from logging import getLogger, basicConfig, NOTSET, INFO
from rich.logging import RichHandler


def configure():
    """Configure logging."""
    basicConfig(
        level=NOTSET,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    getLogger("shinier").setLevel(INFO)
