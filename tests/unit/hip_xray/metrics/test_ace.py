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

import numpy as np

from retuve.classes.draw import Overlay
from retuve.hip_xray.metrics.ace import draw_ace, extend_line, find_ace


def test_find_ace(landmarks_xray_0, expected_xray_metrics):
    ace_index_left, ace_index_right = find_ace(landmarks_xray_0)

    assert isinstance(ace_index_left, float), "ACE Index left should be a float."
    assert isinstance(ace_index_right, float), "ACE Index right should be a float."
    assert (
        0 <= ace_index_left <= 180
    ), "ACE Index left should be between 0 and 180 degrees."
    assert (
        0 <= ace_index_right <= 180
    ), "ACE Index right should be between 0 and 180 degrees."

    assert ace_index_left == expected_xray_metrics["ace_left"]
    assert ace_index_right == expected_xray_metrics["ace_right"]


def test_extend_line():
    p1 = np.array([0, 0])
    p2 = np.array([10, 10])
    left_point, right_point = extend_line(p1, p2, scale=1.2)

    assert isinstance(left_point, np.ndarray), "Left point should be a numpy array."
    assert isinstance(right_point, np.ndarray), "Right point should be a numpy array."
    assert left_point.shape == (2,), "Left point should have 2 dimensions."
    assert right_point.shape == (2,), "Right point should have 2 dimensions."

    assert np.isclose(
        left_point, np.array([-1, -1])
    ).all(), f"Left point should be [-1, -1] but is {left_point}"
    assert np.isclose(
        right_point, np.array([11, 11])
    ).all(), f"Right point should be [11, 11] but is {right_point}"


def test_draw_ace(hip_data_xray_0, img_shape_xray, config_us):
    overlay = Overlay(img_shape_xray, config_us)
    overlay = draw_ace(hip_data_xray_0, overlay, config_us)

    assert isinstance(overlay, Overlay)
