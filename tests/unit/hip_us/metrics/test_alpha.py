import pytest

from retuve.classes.draw import Overlay
from retuve.hip_us.classes.general import LandmarksUS
from retuve.hip_us.metrics.alpha import (
    bad_alpha,
    draw_alpha,
    find_alpha_angle,
    find_alpha_landmarks,
)


@pytest.fixture
def modified_landmarks(landmarks_us_0):
    landmarks_us_0.left = None
    landmarks_us_0.right = None
    landmarks_us_0.apex = None
    return landmarks_us_0


def test_find_alpha_landmarks(
    illium_0, modified_landmarks, config_us, expected_us_metrics, img_shape_us
):
    landmarks = find_alpha_landmarks(illium_0, modified_landmarks, config_us)
    assert isinstance(landmarks, LandmarksUS)
    assert hasattr(landmarks, "left")
    assert hasattr(landmarks, "right")
    assert hasattr(landmarks, "apex")

    # Check the points actually land on the image
    assert 0 <= landmarks.left[0] < img_shape_us[1]
    assert 0 <= landmarks.left[1] < img_shape_us[0]
    assert 0 <= landmarks.right[0] < img_shape_us[1]
    assert 0 <= landmarks.right[1] < img_shape_us[0]
    assert 0 <= landmarks.apex[0] < img_shape_us[1]
    assert 0 <= landmarks.apex[1] < img_shape_us[0]


def test_find_alpha_angle(landmarks_us_0, expected_us_metrics):
    angle = find_alpha_angle(landmarks_us_0)
    assert isinstance(angle, float)
    assert angle >= 0
    assert angle == expected_us_metrics["alpha"]


def test_draw_alpha(hip_data_us_0, config_us):
    overlay = Overlay(shape=(100, 100, 3), config=config_us)
    overlay = draw_alpha(hip_data_us_0, overlay, config_us)
    assert isinstance(overlay, Overlay)
    assert overlay is not None


def test_bad_alpha(hip_data_us_0):
    result = bad_alpha(hip_data_us_0)
    assert isinstance(result, bool)
    assert result is False
