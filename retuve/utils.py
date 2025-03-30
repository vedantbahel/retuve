# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility functions for the Retuve package.
"""

import functools
import logging
import os
import statistics
import sys
from typing import List, Tuple

from retuve.logs import ulogger
from retuve.typehints import MidLine

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    RETUVE_DIR = sys._MEIPASS
else:
    RETUVE_DIR = os.path.dirname(os.path.realpath(__file__))


def register_config_dirs(config, other_dirs=[]):
    hippa_log_file_dir = os.path.dirname(config.api.hippa_logging_file)
    sql_path = os.path.dirname(config.api.db_path)
    dirs = [
        config.api.savedir,
        config.api.upload_dir,
        hippa_log_file_dir,
        sql_path,
    ]

    dirs.extend(other_dirs)
    dirs.extend(config.trak.datasets)
    dirs.extend(config.batch.datasets)

    for dir in dirs:
        if dir and not os.path.exists(dir):
            ulogger.info(f"Creating directory: {dir}")
            os.makedirs(dir)


def rmean(values: List[float]) -> float:
    """
    Calculate the rounded mean of a list of values.

    :param values: The list of values to calculate the mean of.
    :return: The rounded mean of the values.
    """
    return round(statistics.mean(values), 2)


def find_midline_extremes(
    midline: MidLine,
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Finds the left-most and right-most white pixels in the midline.

    :param midline: The midline to find the extremes of.
    :return: The left-most and right-most white pixels.
    """
    # Identifying the left-most and right-most white pixels
    if midline.size > 0:
        left_most = midline[midline[:, 1].argmin()]
        right_most = midline[midline[:, 1].argmax()]
        return left_most, right_most
    else:
        logging.warning("No white pixels found in the image.")
        return None, None


# Global registry to track which functions have shown warnings
_warned_functions = set()


def warning_decorator(alpha=False, beta=False, validated=False, paper_url=None):
    """
    Decorator to print warning messages when decorated functions are run, based on specified flags.
    Each warning is only printed once per function per program run.

    Args:
        alpha (bool): If True, prints an alpha warning message. Defaults to False.
        beta (bool): If True, prints a beta warning message. Defaults to False.
        validated (bool): If True, prints a validated warning message. Defaults to False.
        paper_url (str, optional): URL of the paper related to the beta validation. Defaults to None.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_id = id(func)  # Use function's id as unique identifier

            # Only show warning if this function hasn't been warned about yet
            if func_id not in _warned_functions:
                if alpha:
                    print(
                        f"\nWARNING: {func.__name__} is in early experimentation "
                        "and should not be used for anything outside of "
                        "research by an expert in the field of Hip Dysplasia "
                        "AI. Use it with extreme caution."
                    )
                elif beta:
                    message = (
                        f"\nWARNING: {func.__name__} has limited validation, with at "
                        "least one paper released on a small scale, with "
                        "accepted Inter-class Correlation coefficients (ICC). "
                        "Use with caution, ensuring to read the full paper."
                    )
                    if paper_url:
                        message += f"  Paper URL: {paper_url}"
                    print(message)
                elif validated:
                    print(
                        f"\nWARNING: Using validated function {func.__name__} - use with caution."
                    )

                # Add this function to the set of warned functions
                _warned_functions.add(func_id)

            return func(*args, **kwargs)

        return wrapper

    return decorator
