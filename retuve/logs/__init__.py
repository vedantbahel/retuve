"""
Logging utilities for the project.

Long term, this should be a decorator.
"""

import logging

MS_CONVERSION_FACTOR = 1000

ulogger = logging.getLogger("uvicorn")

# check if logger exists
if not ulogger.hasHandlers():
    ulogger = logging.getLogger()


def log_timings(timings, title=None):
    if title is None:
        title = "Speed:"

    total_time_ms = sum(timings)
    average_time_ms = total_time_ms / len(timings)
    ulogger.info(
        f"{title} {total_time_ms:.2f} s total, "
        f"{average_time_ms*MS_CONVERSION_FACTOR :.2f} ms per frame. "
        f"Max: {max(timings)*MS_CONVERSION_FACTOR:.2f} ms, "
    )
