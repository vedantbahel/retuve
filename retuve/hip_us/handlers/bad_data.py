"""
Handles bad Hip Data Objects by removing outliers and empty frames.
"""

import time
from typing import List

from retuve.hip_us.classes.general import HipDatasUS, HipDataUS
from retuve.hip_us.metrics.alpha import bad_alpha
from retuve.keyphrases.config import Config
from retuve.logs import log_timings


def remove_outliers(hip_datas: HipDatasUS, config: Config) -> List[bool]:
    """
    Remove outliers from the HipDatasUS object.

    :param hip_datas: HipDatasUS object.
    :param config: Config object.

    :return: List of booleans indicating which frames to keep.
    """
    pred_made = [(True if hip.marked() else False) for hip in hip_datas]

    # Use this as a sliding window to find the position where
    # the most Trues fit in the window
    # Get total number of True values
    total_true = sum(pred_made)

    # Sliding window to find the position where the most Trues fit in the window
    max_true = 0
    max_true_index = 0

    for i in range(len(pred_made) - total_true + 1):
        current_window_true = sum(pred_made[i : i + total_true])
        if current_window_true > max_true:
            max_true = current_window_true
            max_true_index = i

    # Create a list of Trues and Falses
    keep = [False] * len(pred_made)
    for i in range(max_true_index, max_true_index + total_true):
        if pred_made[i]:
            keep[i] = True

    return keep


def handle_bad_frames(hip_datas: HipDatasUS, config: Config) -> HipDatasUS:
    """
    Handle bad frames by removing outliers and empty frames.

    :param hip_datas: HipDatasUS object.
    :param config: Config object.

    :return: HipDatasUS object.
    """
    timings = []

    keep = remove_outliers(hip_datas, config)

    for i, hip in enumerate(hip_datas):
        start = time.time()

        empty_hip = HipDataUS(
            frame_no=hip.frame_no,
        )

        timings.append(time.time() - start)

        if not keep[i]:
            hip_datas[i] = empty_hip
            continue

        if (not hip.metrics) or all(
            metric.value == 0 for metric in hip.metrics
        ):
            hip_datas[i] = empty_hip
            continue

        if hip.landmarks is None:
            hip_datas[i] = empty_hip
            continue

        if bad_alpha(hip):
            hip_datas[i] = empty_hip
            continue

    log_timings(timings, title="Bad Frame Handling Speed:")

    return hip_datas
