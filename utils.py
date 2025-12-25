from rich.logging import RichHandler
import logging

# 日志记录
logging.basicConfig(
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.WARNING,
    handlers=[
        RichHandler(
            level=logging.NOTSET,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            tracebacks_suppress=[],
            tracebacks_max_frames=100,
        )
    ],
    force=False,
)

logger = logging.getLogger('Pixai.Art')
logger.setLevel(logging.INFO)
