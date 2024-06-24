"""
Utility functions for the Retuve package.
"""

import logging
import statistics
from typing import List, Tuple

from retuve.typehints import MidLine


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
