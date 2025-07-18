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
import pytest

from retuve.classes.draw import Overlay
from retuve.hip_xray.classes import LandmarksXRay
from retuve.hip_xray.metrics.ihdi import (
    _calculate_grade,
    _draw_side,
    _get_ihdi_lines,
    draw_ihdi,
    find_ihdi,
)
from retuve.utils import find_perpendicular_point


def test_find_ihdi(landmarks_xray_0, expected_xray_metrics):
    """Test the find_ihdi function with valid landmarks."""
    ihdi_left, ihdi_right = find_ihdi(landmarks_xray_0)

    assert isinstance(ihdi_left, int), "IHDI grade left should be an integer."
    assert isinstance(
        ihdi_right, int
    ), "IHDI grade right should be an integer."
    assert 0 <= ihdi_left <= 4, "IHDI grade left should be between 0 and 4."
    assert 0 <= ihdi_right <= 4, "IHDI grade right should be between 0 and 4."

    # Check against expected values from the test data
    assert ihdi_left == expected_xray_metrics["ihdi_left"]
    assert ihdi_right == expected_xray_metrics["ihdi_right"]


def test_find_ihdi_invalid_landmarks():
    """Test find_ihdi with invalid/missing landmarks."""
    # Create landmarks with missing required points
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = None
    landmarks.pel_l_i = (100, 100)
    landmarks.pel_r_i = (200, 100)
    landmarks.pel_r_o = (300, 100)

    ihdi_left, ihdi_right = find_ihdi(landmarks)
    assert ihdi_left == 0, "Should return 0 for invalid landmarks"
    assert ihdi_right == 0, "Should return 0 for invalid landmarks"


def test_find_ihdi_missing_h_points():
    """Test find_ihdi when h_points are missing."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.h_point_l = None
    landmarks.h_point_r = None

    ihdi_left, ihdi_right = find_ihdi(landmarks)
    assert ihdi_left == 0, "Should return 0 when left h_point is missing"
    assert ihdi_right == 0, "Should return 0 when right h_point is missing"


def test_get_ihdi_lines():
    """Test the _get_ihdi_lines helper function."""
    pel_o = (100, 100)
    pel_i = (150, 100)
    h_line_p1 = (150, 100)
    h_line_p2 = (250, 100)
    rotation_angle = 135

    p_line_intercept, d_line = _get_ihdi_lines(
        pel_o, pel_i, h_line_p1, h_line_p2, rotation_angle
    )

    assert isinstance(
        p_line_intercept, np.ndarray
    ), "p_line_intercept should be numpy array"
    assert isinstance(d_line, tuple), "d_line should be a tuple"
    assert len(d_line) == 2, "d_line should contain 2 points"


def test_calculate_grade_grade_1(ihdi_points_left):
    """Test _calculate_grade for Grade I (h_point at or medial to P-line)."""
    h_point = (5, 9)
    pel_o, h_line_p1, h_line_p2, d_line = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)
    grade = _calculate_grade(
        h_point,
        pel_o,
        p_line_intercept,
        d_line,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 1, f"Expected Grade I, got Grade {grade}"


def test_calculate_grade_grade_2(ihdi_points_left):
    """Test _calculate_grade for Grade II (lateral to P-line, medial to D-line)."""
    h_point = (2, 9)
    pel_o, h_line_p1, h_line_p2, d_line = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_grade(
        h_point,
        pel_o,
        p_line_intercept,
        d_line,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 2, f"Expected Grade II, got Grade {grade}"


def test_calculate_grade_grade_3(ihdi_points_left):
    """Test _calculate_grade for Grade III (lateral to D-line, inferior to H-line)."""
    h_point = (2, 7)
    pel_o, h_line_p1, h_line_p2, d_line = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_grade(
        h_point,
        pel_o,
        p_line_intercept,
        d_line,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 3, f"Expected Grade III, got Grade {grade}"


def test_calculate_grade_grade_4(ihdi_points_left):
    """Test _calculate_grade for Grade IV (superior to H-line)."""
    h_point = (1, 5)
    pel_o, h_line_p1, h_line_p2, d_line = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_grade(
        h_point,
        pel_o,
        p_line_intercept,
        d_line,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 4, f"Expected Grade IV, got Grade {grade}"


def test_calculate_grade_right_side(ihdi_points_right):
    """Test _calculate_grade for right side (different medial/lateral logic)."""
    h_point = (8, 9)
    pel_o, h_line_p1, h_line_p2, d_line = ihdi_points_right
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_grade(
        h_point,
        pel_o,
        p_line_intercept,
        d_line,
        h_line_p1,
        h_line_p2,
        is_left_side=False,
    )

    assert grade == 1, f"Expected Grade I for right side, got Grade {grade}"


def test_draw_side(config_xray):
    """Test the _draw_side helper function."""
    overlay = Overlay((500, 500, 3), config_xray)
    d_line = ((100, 100), (200, 200))
    grade_text = "IHDI Grade: 2"
    text_pos = (150, 150)

    # Should not raise an exception
    _draw_side(overlay, d_line, grade_text, text_pos)

    assert isinstance(overlay, Overlay)


def test_draw_ihdi(hip_data_xray_0, img_shape_xray, config_xray):
    """Test the draw_ihdi function."""
    overlay = Overlay(img_shape_xray, config_xray)
    overlay = draw_ihdi(hip_data_xray_0, overlay, config_xray)

    assert isinstance(overlay, Overlay)


def test_draw_ihdi_invalid_landmarks(img_shape_xray, config_xray):
    """Test draw_ihdi with invalid landmarks."""
    from retuve.hip_xray.classes import HipDataXray

    hip = HipDataXray()
    hip.landmarks = LandmarksXRay()
    hip.landmarks.pel_l_o = None  # Invalid landmark
    hip.metrics = [None] * 8  # Mock metrics array

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_ihdi(hip, overlay, config_xray)

    assert isinstance(result, Overlay)


def test_draw_ihdi_missing_h_points(img_shape_xray, config_xray):
    """Test draw_ihdi when h_points are missing."""
    from retuve.hip_xray.classes import HipDataXray

    hip = HipDataXray()
    hip.landmarks = LandmarksXRay()
    hip.landmarks.pel_l_o = (100, 100)
    hip.landmarks.pel_l_i = (150, 100)
    hip.landmarks.pel_r_i = (250, 100)
    hip.landmarks.pel_r_o = (300, 100)
    hip.landmarks.h_point_l = None
    hip.landmarks.h_point_r = None
    hip.metrics = [None] * 8  # Mock metrics array

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_ihdi(hip, overlay, config_xray)

    assert isinstance(result, Overlay)
