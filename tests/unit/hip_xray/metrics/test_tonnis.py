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

from retuve.classes.draw import Overlay
from retuve.hip_xray.classes import LandmarksXRay
from retuve.hip_xray.metrics.tonnis import (
    _calculate_tonnis_grade,
    _draw_tonnis_side,
    draw_tonnis,
    find_tonnis,
)
from retuve.utils import find_perpendicular_point


def test_find_tonnis(landmarks_xray_0, expected_xray_metrics):
    """Test the find_tonnis function with valid landmarks."""
    tonnis_left, tonnis_right = find_tonnis(landmarks_xray_0)

    assert isinstance(
        tonnis_left, int
    ), "Tonnis grade left should be an integer."
    assert isinstance(
        tonnis_right, int
    ), "Tonnis grade right should be an integer."
    assert (
        0 <= tonnis_left <= 4
    ), "Tonnis grade left should be between 0 and 4."
    assert (
        0 <= tonnis_right <= 4
    ), "Tonnis grade right should be between 0 and 4."

    # Check against expected values from the test data
    assert tonnis_left == expected_xray_metrics["tonnis_grade_left"]
    assert tonnis_right == expected_xray_metrics["tonnis_grade_right"]


def test_find_tonnis_invalid_landmarks():
    """Test find_tonnis with invalid/missing landmarks."""
    # Create landmarks with missing required points
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = None
    landmarks.pel_l_i = (100, 100)
    landmarks.pel_r_i = (200, 100)
    landmarks.pel_r_o = (300, 100)

    tonnis_left, tonnis_right = find_tonnis(landmarks)
    assert tonnis_left == 0, "Should return 0 for invalid landmarks"
    assert tonnis_right == 0, "Should return 0 for invalid landmarks"


def test_find_tonnis_missing_femoral_points():
    """Test find_tonnis when femoral points are missing."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.fem_l = None
    landmarks.fem_r = None

    tonnis_left, tonnis_right = find_tonnis(landmarks)
    assert (
        tonnis_left == 0
    ), "Should return 0 when left femoral point is missing"
    assert (
        tonnis_right == 0
    ), "Should return 0 when right femoral point is missing"


def test_calculate_tonnis_grade_grade_1(ihdi_points_left):
    """Test _calculate_tonnis_grade for Grade I (medial to P-line, below SMA-line)."""
    fem_point = (5, 9)
    pel_o, h_line_p1, h_line_p2, _ = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_tonnis_grade(
        fem_point,
        pel_o,
        p_line_intercept,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 1, f"Expected Grade I, got Grade {grade}"


def test_calculate_tonnis_grade_grade_2(ihdi_points_left):
    """Test _calculate_tonnis_grade for Grade II (lateral to P-line, below SMA-line)."""
    fem_point = (2, 9)
    pel_o, h_line_p1, h_line_p2, _ = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_tonnis_grade(
        fem_point,
        pel_o,
        p_line_intercept,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 2, f"Expected Grade II, got Grade {grade}"


def test_calculate_tonnis_grade_grade_3(ihdi_points_left):
    """Test _calculate_tonnis_grade for Grade III (on SMA-line)."""
    fem_point = (1, 3)
    pel_o, h_line_p1, h_line_p2, _ = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_tonnis_grade(
        fem_point,
        pel_o,
        p_line_intercept,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 3, f"Expected Grade III, got Grade {grade}"


def test_calculate_tonnis_grade_grade_4(ihdi_points_left):
    """Test _calculate_tonnis_grade for Grade IV (above SMA-line)."""
    fem_point = (1, 2)
    pel_o, h_line_p1, h_line_p2, _ = ihdi_points_left
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_tonnis_grade(
        fem_point,
        pel_o,
        p_line_intercept,
        h_line_p1,
        h_line_p2,
        is_left_side=True,
    )

    assert grade == 4, f"Expected Grade IV, got Grade {grade}"


def test_calculate_tonnis_grade_right_side(ihdi_points_right):
    """Test _calculate_tonnis_grade for right side (different medial/lateral logic)."""
    fem_point = (8, 9)
    pel_o, h_line_p1, h_line_p2, _ = ihdi_points_right
    p_line_intercept = find_perpendicular_point(h_line_p1, h_line_p2, pel_o)

    grade = _calculate_tonnis_grade(
        fem_point,
        pel_o,
        p_line_intercept,
        h_line_p1,
        h_line_p2,
        is_left_side=False,
    )

    assert grade == 1, f"Expected Grade I for right side, got Grade {grade}"


def test_draw_tonnis_side(config_xray):
    """Test the _draw_tonnis_side helper function."""
    overlay = Overlay((500, 500, 3), config_xray)
    pel_o = (100, 100)
    h_line_p1 = (150, 100)
    h_line_p2 = (250, 100)
    grade_text = "Tonnis Grade: 2"

    # Should not raise an exception
    _draw_tonnis_side(overlay, pel_o, h_line_p1, h_line_p2, grade_text)

    assert isinstance(overlay, Overlay)


def test_draw_tonnis(hip_data_xray_0, img_shape_xray, config_xray):
    """Test the draw_tonnis function."""
    overlay = Overlay(img_shape_xray, config_xray)
    overlay = draw_tonnis(hip_data_xray_0, overlay, config_xray)

    assert isinstance(overlay, Overlay)


def test_draw_tonnis_invalid_landmarks(img_shape_xray, config_xray):
    """Test draw_tonnis with invalid landmarks."""
    from retuve.hip_xray.classes import HipDataXray

    hip = HipDataXray()
    hip.landmarks = LandmarksXRay()
    hip.landmarks.pel_l_o = None  # Invalid landmark
    hip.metrics = [None] * 8  # Mock metrics array

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_tonnis(hip, overlay, config_xray)

    assert isinstance(result, Overlay)


def test_draw_tonnis_missing_femoral_points(img_shape_xray, config_xray):
    """Test draw_tonnis when femoral points are missing."""
    from retuve.hip_xray.classes import HipDataXray

    hip = HipDataXray()
    hip.landmarks = LandmarksXRay()
    hip.landmarks.pel_l_o = (100, 100)
    hip.landmarks.pel_l_i = (150, 100)
    hip.landmarks.pel_r_i = (250, 100)
    hip.landmarks.pel_r_o = (300, 100)
    hip.landmarks.fem_l = None
    hip.landmarks.fem_r = None
    hip.metrics = [None] * 8  # Mock metrics array

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_tonnis(hip, overlay, config_xray)

    assert isinstance(result, Overlay)
