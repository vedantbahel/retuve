"""
Utility functions for the Retuve package.
"""

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
