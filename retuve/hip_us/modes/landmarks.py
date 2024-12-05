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
All code relating to going from measured landmarks to metrics is in this file.
"""

import time
from typing import List, Tuple

from retuve.classes.metrics import Metric2D
from retuve.hip_us.classes.general import HipDatasUS, HipDataUS, LandmarksUS
from retuve.hip_us.metrics.alpha import find_alpha_angle
from retuve.hip_us.metrics.coverage import find_coverage
from retuve.hip_us.metrics.curvature import find_curvature
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import MetricUS
from retuve.logs import log_timings


def landmarks_2_metrics_us(
    list_landmarks: List[LandmarksUS],
    shape: Tuple[int, int],
    config: Config,
) -> HipDatasUS:
    """
    Converts a list of landmarks to a list of metrics.

    :param list_landmarks: A list of landmarks.
    :param shape: The shape of the image.
    :param config: The configuration object.

    :return: A list of metrics.
    """
    hips = HipDatasUS()
    timings = []

    for frame_no, landmarks in enumerate(list_landmarks):
        start = time.time()

        alpha = find_alpha_angle(landmarks)
        coverage = find_coverage(landmarks)
        curvature = find_curvature(landmarks, shape, config)

        metrics = []

        for name, value in [
            (MetricUS.ALPHA, alpha),
            (MetricUS.COVERAGE, coverage),
            (MetricUS.CURVATURE, curvature),
        ]:
            if name in config.hip.measurements:
                metrics.append(Metric2D(name, value))

        hip = HipDataUS(
            landmarks=landmarks,
            metrics=metrics,
            frame_no=frame_no,
        )

        hips.append(hip)
        timings.append(time.time() - start)

    log_timings(timings, title="Landmarks->Metrics Speed:")

    return hips
