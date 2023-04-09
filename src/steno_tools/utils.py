"""Utility functions."""

import logging


def setup_logging(verbosity):
    """Configure the logger.

    Args:
        verbosity: Integer specifying at what level logs should be emitted.
    """

    log_level = logging.WARNING
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG

    log_format = "%(levelname)s: %(message)s"
    logging.basicConfig(level=log_level, format=log_format)
