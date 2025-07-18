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
from retuve.hip_xray.metrics.wiberg import draw_wiberg, find_wiberg
from retuve.utils import angle_between_lines, find_perpendicular_point


def test_find_wiberg(landmarks_xray_0, expected_xray_metrics):
    """Test the find_wiberg function with valid landmarks."""
    wiberg_left, wiberg_right = find_wiberg(landmarks_xray_0)

    assert isinstance(wiberg_left, float) or isinstance(
        wiberg_left, int
    ), f"Wiberg index left should be a float or int, got {wiberg_left}"
    assert isinstance(wiberg_right, float) or isinstance(
        wiberg_right, int
    ), f"Wiberg index right should be a float or int, got {wiberg_right}"
    assert (
        0 <= wiberg_left <= 180
    ), "Wiberg index left should be between 0 and 180 degrees."
    assert (
        0 <= wiberg_right <= 180
    ), "Wiberg index right should be between 0 and 180 degrees."

    # Check against expected values from the test data
    assert wiberg_left == expected_xray_metrics["wiberg_left"]
    assert wiberg_right == expected_xray_metrics["wiberg_right"]


def test_find_wiberg_invalid_landmarks():
    """Test find_wiberg with invalid/missing landmarks."""
    # Create landmarks with missing required points
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = None
    landmarks.pel_l_i = (100, 100)
    landmarks.pel_r_i = (200, 100)
    landmarks.pel_r_o = (300, 100)

    wiberg_left, wiberg_right = find_wiberg(landmarks)
    assert wiberg_left == 0, "Should return 0 for invalid landmarks"
    assert wiberg_right == 0, "Should return 0 for invalid landmarks"


def test_find_wiberg_missing_h_points():
    """Test find_wiberg when h_points are missing."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.h_point_l = None
    landmarks.h_point_r = None

    wiberg_left, wiberg_right = find_wiberg(landmarks)
    assert wiberg_left == 0, "Should return 0 when left h_point is missing"
    assert wiberg_right == 0, "Should return 0 when right h_point is missing"


def test_find_wiberg_left_side_only():
    """Test find_wiberg when only left h_point is available."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.h_point_l = (120, 150)
    landmarks.h_point_r = None

    wiberg_left, wiberg_right = find_wiberg(landmarks)
    assert wiberg_left > 0, "Should calculate left Wiberg index"
    assert wiberg_right == 0, "Should return 0 when right h_point is missing"


def test_find_wiberg_right_side_only():
    """Test find_wiberg when only right h_point is available."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.h_point_l = None
    landmarks.h_point_r = (280, 150)

    wiberg_left, wiberg_right = find_wiberg(landmarks)
    assert wiberg_left == 0, "Should return 0 when left h_point is missing"
    assert wiberg_right > 0, "Should calculate right Wiberg index"


def test_find_wiberg_angle_calculation():
    """Test that Wiberg index correctly calculates angles between lines."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.h_point_l = (120, 150)
    landmarks.h_point_r = (280, 150)

    wiberg_left, wiberg_right = find_wiberg(landmarks)

    # Verify the calculation by manually computing the expected angles
    p_line_intercept_left = find_perpendicular_point(
        landmarks.pel_l_i, landmarks.pel_r_i, landmarks.pel_l_o
    )
    p_line_left = (landmarks.pel_l_o, p_line_intercept_left)
    wiberg_line_left = (landmarks.pel_l_o, landmarks.h_point_l)
    expected_left = angle_between_lines(p_line_left, wiberg_line_left)
    expected_left = round(expected_left, 1)

    p_line_intercept_right = find_perpendicular_point(
        landmarks.pel_r_i, landmarks.pel_l_i, landmarks.pel_r_o
    )
    p_line_right = (landmarks.pel_r_o, p_line_intercept_right)
    wiberg_line_right = (landmarks.pel_r_o, landmarks.h_point_r)
    expected_right = angle_between_lines(p_line_right, wiberg_line_right)
    expected_right = round(expected_right, 1)

    assert (
        abs(wiberg_left - expected_left) < 0.1
    ), f"Left Wiberg index mismatch: {wiberg_left} vs {expected_left}"
    assert (
        abs(wiberg_right - expected_right) < 0.1
    ), f"Right Wiberg index mismatch: {wiberg_right} vs {expected_right}"


def test_find_wiberg_rounding():
    """Test that Wiberg indices are properly rounded to 1 decimal place."""
    landmarks = LandmarksXRay()
    landmarks.pel_l_o = (100, 100)
    landmarks.pel_l_i = (150, 100)
    landmarks.pel_r_i = (250, 100)
    landmarks.pel_r_o = (300, 100)
    landmarks.h_point_l = (120, 150)
    landmarks.h_point_r = (280, 150)

    wiberg_left, wiberg_right = find_wiberg(landmarks)

    # Check that values are rounded to 1 decimal place
    assert wiberg_left == round(
        wiberg_left, 1
    ), "Left Wiberg index should be rounded to 1 decimal place"
    assert wiberg_right == round(
        wiberg_right, 1
    ), "Right Wiberg index should be rounded to 1 decimal place"


def test_draw_wiberg(hip_data_xray_0, img_shape_xray, config_xray):
    """Test the draw_wiberg function."""
    overlay = Overlay(img_shape_xray, config_xray)
    overlay = draw_wiberg(hip_data_xray_0, overlay, config_xray)

    assert isinstance(overlay, Overlay)


def test_draw_wiberg_invalid_landmarks(img_shape_xray, config_xray):
    """Test draw_wiberg with invalid landmarks."""
    from retuve.hip_xray.classes import HipDataXray

    hip = HipDataXray()
    hip.landmarks = LandmarksXRay()
    hip.landmarks.pel_l_o = None  # Invalid landmark
    hip.metrics = [None] * 8  # Mock metrics array

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_wiberg(hip, overlay, config_xray)

    assert isinstance(result, Overlay)


def test_draw_wiberg_missing_h_points(img_shape_xray, config_xray):
    """Test draw_wiberg when h_points are missing."""
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
    result = draw_wiberg(hip, overlay, config_xray)

    assert isinstance(result, Overlay)


def test_draw_wiberg_left_side_only(hip_data_xray_0, img_shape_xray, config_xray):
    """Test draw_wiberg when only left h_point is available."""
    hip_data_xray_0.landmarks.h_point_l = (120, 150)

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_wiberg(hip_data_xray_0, overlay, config_xray)

    assert isinstance(result, Overlay)


def test_draw_wiberg_right_side_only(hip_data_xray_0, img_shape_xray, config_xray):
    """Test draw_wiberg when only right h_point is available."""
    hip_data_xray_0.landmarks.h_point_r = (280, 150)

    overlay = Overlay(img_shape_xray, config_xray)
    result = draw_wiberg(hip_data_xray_0, overlay, config_xray)

    assert isinstance(result, Overlay)
