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
Metric: Acentabular Index (ACE Index)
"""

from typing import Literal

import numpy as np
from radstract.math import smart_find_intersection

from retuve.draw import Overlay
from retuve.hip_xray.classes import HipDataXray, LandmarksXRay
from retuve.keyphrases.config import Config


def find_ace(landmarks: LandmarksXRay) -> tuple[float, float]:
    """
    Calculate the Acentabular Index (ACE Index) for both hips.

    :param landmarks: The Landmarks of the Hip
    :return: The ACE Index for both hips
    """
    intersection_left = smart_find_intersection(
        landmarks.pel_l_o, landmarks.pel_l_i, landmarks.fem_l, landmarks.fem_r
    )
    intersection_right = smart_find_intersection(
        landmarks.pel_r_o, landmarks.pel_r_i, landmarks.fem_l, landmarks.fem_r
    )

    A, B, C = (
        np.array(landmarks.pel_l_o),
        np.array(landmarks.pel_l_i),
        np.array(intersection_right),
    )
    AB = np.linalg.norm(A - B)
    BC = np.linalg.norm(B - C)
    AC = np.linalg.norm(A - C)

    ace_index_left = np.arccos((BC**2 + AB**2 - AC**2) / (2 * BC * AB))

    ace_index_left = round(180 - np.degrees(ace_index_left), 1)

    A, B, C = (
        np.array(landmarks.pel_r_o),
        np.array(landmarks.pel_r_i),
        np.array(intersection_left),
    )
    AB = np.linalg.norm(A - B)
    BC = np.linalg.norm(B - C)
    AC = np.linalg.norm(A - C)

    ace_index_right = np.arccos((BC**2 + AB**2 - AC**2) / (2 * BC * AB))

    ace_index_right = round(180 - np.degrees(ace_index_right), 1)

    if not (5 < ace_index_left < 50):
        ace_index_left = 0

    if not (5 < ace_index_right < 50):
        ace_index_right = 0

    return ace_index_left, ace_index_right


def extend_line(
    p1: list,
    p2: list,
    scale: float = 1.2,
    direction: Literal["both", "up", "down"] = "both",
):
    """
    Extend the line from p1 to p2 by a scale factor (default 10%)
    in specified direction ('up', 'down', 'both').

    :param p1: The first point of the line
    :param p2: The second point of the line
    :param scale: The scale factor
    :param direction: The direction to extend the lines
    """
    direction_vector = np.array(p2) - np.array(p1)
    left_point = (
        np.array(p1) - direction_vector * (scale - 1)
        if direction in ["up", "both"]
        else np.array(p1)
    )
    right_point = (
        np.array(p2) + direction_vector * (scale - 1)
        if direction in ["down", "both"]
        else np.array(p2)
    )

    return left_point, right_point


def draw_ace(hip: HipDataXray, overlay: Overlay, config: Config):
    """
    Draw the Acentabular Index (ACE Index) on the X-Ray.

    :param hip: The Hip Data
    :param overlay: The Overlay
    :param config: The Config

    :return: The Drawn Overlay
    """
    landmarks = hip.landmarks

    if not landmarks.fem_l:
        return overlay

    # Intersect and extend lines
    intersection_left = smart_find_intersection(
        landmarks.pel_l_o, landmarks.pel_l_i, landmarks.fem_l, landmarks.fem_r
    )
    intersection_right = smart_find_intersection(
        landmarks.pel_r_o, landmarks.pel_r_i, landmarks.fem_l, landmarks.fem_r
    )

    new_H_line = extend_line(landmarks.fem_l, landmarks.fem_r, scale=1.2)
    new_A_line = extend_line(
        landmarks.pel_l_o, intersection_left, scale=1.3, direction="up"
    )
    new_B_line = extend_line(
        landmarks.pel_r_o, intersection_right, scale=1.3, direction="up"
    )

    overlay.draw_lines([new_H_line, new_A_line, new_B_line])

    # Draw ace_index_left and ace_index_right
    overlay.draw_text(
        f"ACE Index: {hip.metrics[0].value}",
        landmarks.fem_l[0] - 150,
        (landmarks.fem_l[1] + 10),
    )

    overlay.draw_text(
        f"ACE Index: {hip.metrics[1].value}",
        landmarks.fem_r[0] - 100,
        (landmarks.fem_r[1] + 10),
    )

    return overlay
