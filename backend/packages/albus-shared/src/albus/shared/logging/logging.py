# /// script
# dependencies = [
#   "structlog",
#   "rich",
# ]
# ///

import logging.config
import sys

import structlog
from structlog.processors import CallsiteParameter


def extract_from_record(_, __, event_dict):
    """
    Extract thread and process names and add them to the event dict.
    """
    record: logging.LogRecord = event_dict["_record"]
    event_dict["filepath"] = record.pathname
    event_dict["thread_name"] = record.threadName
    # event_dict["thread"] = record.thread
    event_dict["process_name"] = record.processName
    # event_dict["filename"] = record.filename
    event_dict["lineno"] = record.lineno
    event_dict["func_name"] = record.funcName
    event_dict["module"] = record.name

    return event_dict


# https://www.structlog.org/en/stable/standard-library.html
# DX
def setup_logging(use_json: bool = False):
    formatter = "colored" if sys.stderr.isatty() and not use_json else "json"
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        # Add extra attributes of LogRecord objects to the event dictionary
        # so that values passed in the extra parameter of log methods pass
        # through to log output.
        structlog.stdlib.ExtraAdder(),
        structlog.processors.CallsiteParameterAdder(
            parameters={
                CallsiteParameter.FILENAME,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.MODULE,
                CallsiteParameter.PATHNAME,
                CallsiteParameter.PROCESS,
                CallsiteParameter.PROCESS_NAME,
                CallsiteParameter.THREAD,
                CallsiteParameter.THREAD_NAME,
            },
            additional_ignores=None,
        ),
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        extract_from_record,
                        structlog.processors.format_exc_info,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.TimeStamper(fmt="iso", utc=True),
                        structlog.processors.dict_tracebacks,
                        structlog.processors.EventRenamer("message"),
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        extract_from_record,
                        # structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                        structlog.processors.TimeStamper(fmt="iso", utc=False),
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(colors=True),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": formatter,
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "httpx": {"level": "WARN"},
                "httpcore": {"level": "WARN"},
                "PIL": {"level": "WARN"},
            },
        }
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def run():
    setup_logging()
    logger = structlog.get_logger()
    logger.info("main", main="test")
    logger.warn("main warn", main="warn test")


if __name__ == "__main__":
    # Color Logging
    # uv run log.py

    # JSON logging
    # uv run log.py 2>&1 | cat
    run()