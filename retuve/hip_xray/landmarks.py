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
This module contains the function to convert landmarks to metrics for hip x-ray.
"""

import time
from typing import List

from retuve.classes.metrics import Metric2D
from retuve.hip_xray.classes import HipDataXray, LandmarksXRay
from retuve.hip_xray.metrics.ace import find_ace
from retuve.keyphrases.config import Config
from retuve.logs import log_timings


def landmarks_2_metrics_xray(
    list_landmarks: List[LandmarksXRay],
    config: Config,
) -> List[HipDataXray]:
    """
    Convert the landmarks to metrics for hip x-ray

    :param list_landmarks: The List of Landmarks
    :param config: The Config

    :return: The List of Hip Data
    """
    hips = []
    timings = []

    for frame_no, landmarks in enumerate(list_landmarks):
        start = time.time()

        hip = HipDataXray()

        if landmarks.fem_l is None:
            ace_l, ace_r = None, None
            hip.recorded_error.append("No landmarks found.")
        else:
            ace_l, ace_r = find_ace(landmarks)

        for name, value in [
            (
                "ace_index_left",
                ace_l,
            ),
            (
                "ace_index_right",
                ace_r,
            ),
        ]:
            hip.metrics.append(Metric2D(name, value))

        hip.landmarks = landmarks
        hip.frame_no = frame_no

        hips.append(hip)
        timings.append(time.time() - start)

    log_timings(timings, title="Landmarks->Metrics Speed:")

    return hips
