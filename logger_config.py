import functools
from typing import Any, Callable, TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from loguru import Record


def setup_logger():
    # Remove the default logging handler to stderr
    logger.remove()
    logger.add("logs/html_parser.log", mode="w", level="DEBUG", filter="browser_html.html_parser")
    logger.add("logs/document_layout.log", mode="w", level="DEBUG", filter="browser_layout.document_layout")
    logger.add("logs/browser_tab.log", mode="w", level="DEBUG", filter="browser_tab")
    logger.add("logs/css_parser.log", mode="w", level="DEBUG", filter="browser_css.css_parser")
    logger.add(
        "logs/network.log",
        mode="w",
        level="DEBUG",
        filter="browser_network.network",
        format="{file}:{function}:{line} - {message}",
    )

    # logger.add(
    #     "logs/css_files.log",
    #     mode="w",
    #     level="DEBUG",
    #     filter=lambda record: "file_name" in record["extra"] and record["extra"]["file_name"] == "css_files",
    # )


def benchmark(func: Callable[..., Any], random_arg: str) -> Callable[..., Any]:
    @functools.wraps(func)  # Makes func.__name__ return the name of the wrapped function rather than 'wrapper'
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(args)
        value = func(*args, **kwargs)
        logger.info(value)
        return value

    return wrapper
