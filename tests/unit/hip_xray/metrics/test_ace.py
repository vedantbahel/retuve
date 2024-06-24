import numpy as np

from retuve.classes.draw import Overlay
from retuve.hip_xray.metrics.ace import draw_ace, extend_line, find_ace


def test_find_ace(landmarks_xray_0, expected_xray_metrics):
    ace_index_left, ace_index_right = find_ace(landmarks_xray_0)

    assert isinstance(
        ace_index_left, float
    ), "ACE Index left should be a float."
    assert isinstance(
        ace_index_right, float
    ), "ACE Index right should be a float."
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

    assert isinstance(
        left_point, np.ndarray
    ), "Left point should be a numpy array."
    assert isinstance(
        right_point, np.ndarray
    ), "Right point should be a numpy array."
    assert left_point.shape == (2,), "Left point should have 2 dimensions."
    assert right_point.shape == (2,), "Right point should have 2 dimensions."

    assert np.isclose(left_point, np.array([-2, -2])).all()
    assert np.isclose(right_point, np.array([12, 12])).all()


def test_draw_ace(hip_data_xray_0, img_shape_xray, config_us):
    overlay = Overlay(img_shape_xray, config_us)
    overlay = draw_ace(hip_data_xray_0, overlay, config_us)

    assert isinstance(overlay, Overlay)
