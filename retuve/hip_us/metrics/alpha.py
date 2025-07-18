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
Metric: Alpha Angle

"""

import numpy as np

from retuve.classes.draw import Overlay
from retuve.classes.seg import SegObject
from retuve.hip_us.classes.general import HipDataUS, LandmarksUS
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import MetricUS
from retuve.utils import find_midline_extremes, warning_decorator

# To move the apex point left or right
APEX_RIGHT_FACTOR = 0


def find_alpha_landmarks(
    illium: SegObject, landmarks: LandmarksUS, config: Config
) -> LandmarksUS:
    """
    Algorithm to find the landmarks for the Alpha Angle.

    :param illium: SegObject: The Illium SegObject.
    :param landmarks: LandmarksUS: The landmarks object.
    :param config: Config: The Config

    :return: LandmarksUS: The updated landmarks object.
    """
    if not (
        illium
        and any(m in config.hip.measurements for m in MetricUS.ALL())
        and illium.mask is not None
    ):
        return landmarks

    left_most, right_most = find_midline_extremes(illium.midline_moved)

    if (
        right_most is None
        or left_most is None
        or (right_most[1] - left_most[1]) == 0
    ):
        return landmarks

    # get the equation for the line between the two extreme points
    # y = mx + b
    m = (right_most[0] - left_most[0]) / (right_most[1] - left_most[1])
    b = left_most[0] - m * left_most[1]

    # if m is 0, return landmarks
    if m == 0:
        return landmarks

    # find the height

    # find the orthogonal line to the line between the two extreme points
    # y = -1/m * x + b
    m_orth = -1 / m
    # for each point along the line, find the distance between that point and the

    points_on_line = np.array(
        [
            [x, m * x + b]
            for x in range(int(left_most[1]), int(right_most[1]), 1)
        ]
    )

    # Convert white_points to a convenient shape for vector operations
    midline_moved = np.array(illium.midline_moved)[
        :, ::-1
    ]  # Reverse each point only once

    # Create an array for b_orth values for each point in points_on_line
    b_orth_array = points_on_line[:, 1] - m_orth * points_on_line[:, 0]

    # Calculate y_values on the orthogonal line for each point in points_on_line
    y_values_orth_line = (
        m_orth * midline_moved[:, 0] + b_orth_array[:, np.newaxis]
    )

    # Check which white points are close to each orthogonal line
    close_points = np.isclose(
        y_values_orth_line, midline_moved[:, 1], atol=0.8
    )

    # Calculate distances for all point pairs
    distances = np.linalg.norm(
        points_on_line[:, np.newaxis, :] - midline_moved, axis=2
    )

    # Mask distances with close_points to consider only relevant distances
    masked_distances = np.where(close_points, distances, 0)

    # Find the maximum distance and the corresponding points
    max_distance = np.max(masked_distances)
    max_distance = np.max(masked_distances)
    if max_distance > 0:
        point_index, apex_point_index = np.unravel_index(
            np.argmax(masked_distances), masked_distances.shape
        )
        best_point = tuple(points_on_line[point_index])
        # Check APEX_RIGHT_FACTOR is within bounds
        if apex_point_index + APEX_RIGHT_FACTOR < len(midline_moved):
            factor = APEX_RIGHT_FACTOR
        else:
            # max possible factor
            factor = len(midline_moved) - apex_point_index - 1

        best_apex_point = tuple(midline_moved[apex_point_index + factor])

        left_most, right_most = find_midline_extremes(illium.midline_moved)
        if right_most is None or left_most is None:
            return landmarks

        left_most, right_most = tuple(reversed(left_most)), tuple(
            reversed(right_most)
        )
        mid_x = (left_most[0] + right_most[0]) / 2
        if (
            (best_apex_point[1] < best_point[1])  # apex above line
            and right_most[0] > best_apex_point[0]  # apex left of right point
            and best_apex_point[0] > mid_x  # mid_x left of apex
        ):
            # re-calculate the left and right points from original midline

            landmarks.left = left_most
            landmarks.right = right_most
            landmarks.apex = best_apex_point

    # reversed because cv2 uses (y, x)??
    return landmarks


@warning_decorator(alpha=True)
def find_alpha_angle(points: LandmarksUS) -> float:
    """
    Calculate the Alpha Angle.

    :param points: LandmarksUS: The landmarks object.

    :return: float: The Alpha Angle.
    """
    if not (points and points.left and points.apex and points.right):
        return 0

    # find angle ABC of points
    A, B, C = (
        np.array(points.left),
        np.array(points.apex),
        np.array(points.right),
    )
    AB = np.linalg.norm(A - B)
    BC = np.linalg.norm(B - C)
    AC = np.linalg.norm(A - C)
    angle = np.arccos((BC**2 + AB**2 - AC**2) / (2 * BC * AB))

    angle = np.degrees(angle)
    angle = round((180 - angle), 1)

    return round(angle, 2)


def draw_alpha(hip: HipDataUS, overlay: Overlay, config: Config) -> Overlay:
    """
    Draw the Alpha Angle on the Overlay.

    :param hip: HipDataUS: The Hip Data.
    :param overlay: Overlay: The Overlay.
    :param config: Config: The Config.

    :return: Overlay: The updated Overlay.
    """
    alpha = hip.get_metric(MetricUS.ALPHA)
    if alpha != 0:
        m1 = (hip.landmarks.apex[1] - hip.landmarks.left[1]) / (
            hip.landmarks.apex[0] - hip.landmarks.left[0]
        )
        m2 = (hip.landmarks.right[1] - hip.landmarks.apex[1]) / (
            hip.landmarks.right[0] - hip.landmarks.apex[0]
        )

        b1 = hip.landmarks.apex[1] - m1 * hip.landmarks.apex[0]
        b2 = hip.landmarks.apex[1] - m2 * hip.landmarks.apex[0]

        # x2 to account for difference in gradient
        new_right_apex = (
            hip.landmarks.apex[0] + 350,
            m1 * (hip.landmarks.apex[0] + 350) + b1,
        )
        new_right_landmark = (
            hip.landmarks.right[0],
            m2 * (hip.landmarks.right[0]) + b2,
        )

        overlay.draw_lines(
            (
                (hip.landmarks.left, new_right_apex),
                (hip.landmarks.apex, new_right_landmark),
            ),
        )

        if config.visuals.display_full_metric_names:
            title = "Alpha Angle"
        else:
            title = "a"

        overlay.draw_text(
            f"{title}: {alpha}",
            int(hip.landmarks.left[0]),
            int(hip.landmarks.left[1] - 40),
            header="h2",
        )

    return overlay


def bad_alpha(hip: HipDataUS) -> bool:
    """
    Check if the Alpha Angle is bad.

    :param hip: HipDataUS: The Hip Data.

    :return: bool: True if the Alpha Angle is bad.
    """

    if (
        hip.get_metric(MetricUS.ALPHA) < 20
        or hip.get_metric(MetricUS.ALPHA) > 100
    ):
        return True

    return False
