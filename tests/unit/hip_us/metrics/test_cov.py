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
from retuve.hip_us.classes.general import LandmarksUS
from retuve.hip_us.metrics.coverage import (
    draw_coverage,
    find_cov_landmarks,
    find_coverage,
)


@pytest.fixture
def modified_landmarks(landmarks_us_0):
    landmarks_us_0.point_D = None
    landmarks_us_0.point_d = None
    landmarks_us_0.mid_cov_point = None
    return landmarks_us_0


def test_find_cov_landmarks_with_valid_data(femoral_0, modified_landmarks, config_us):
    landmarks = find_cov_landmarks(femoral_0, modified_landmarks, config_us)
    assert landmarks.point_d is not None
    assert landmarks.point_D is not None
    assert landmarks.mid_cov_point is not None


def test_find_cov_landmarks_with_no_femoral(modified_landmarks, config_us):
    landmarks = find_cov_landmarks(None, modified_landmarks, config_us)
    assert landmarks.point_d is None
    assert landmarks.point_D is None
    assert landmarks.mid_cov_point is None


def test_find_coverage_with_valid_data():
    landmarks = LandmarksUS(
        apex=(0, 0),
        left=(0, 1),
        point_d=(0, 0),
        point_D=(0, 2),
        mid_cov_point=(0, 1),
    )
    coverage = find_coverage(landmarks)
    assert coverage == 0.5


def test_find_coverage_with_no_landmarks():
    coverage = find_coverage(None)
    assert coverage == 0


def test_find_coverage_with_no_mid_cov_point():
    landmarks = LandmarksUS(
        apex=(0, 0),
        left=(0, 1),
        point_d=(0, 0),
        point_D=(0, 2),
        mid_cov_point=None,
    )
    coverage = find_coverage(landmarks)
    assert coverage == 0


def test_draw_coverage_with_valid_data(hip_data_us_0, config_us):
    overlay = Overlay(shape=(100, 100, 3), config=config_us)
    overlay = draw_coverage(hip_data_us_0, overlay, config_us)
    assert overlay is not None
