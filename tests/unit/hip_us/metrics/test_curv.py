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

import pytest

from retuve.classes.draw import Overlay
from retuve.hip_us.metrics.curvature import draw_curvature, find_curvature
from retuve.keyphrases.enums import Curvature


@pytest.fixture
def modified_curvature_data(landmarks_us_0, results_us_0):

    shape = results_us_0.img.shape
    return landmarks_us_0, shape


def test_find_curvature_radist(modified_curvature_data, config_us, expected_us_metrics):
    landmarks, shape = modified_curvature_data
    config = config_us

    config.hip.curvature_method = Curvature.RADIST

    curvature = find_curvature(landmarks, shape, config)

    assert isinstance(curvature, float)
    assert curvature > 0
    assert curvature == expected_us_metrics["curvature"]


def test_find_curvature_no_landmarks(config_us, results_us_0):
    landmarks = None
    shape = results_us_0.img.shape

    curvature = find_curvature(landmarks, shape, config_us)

    assert curvature == 0


def test_draw_curvature(hip_data_us_0, results_us_0, config_us):
    overlay = Overlay(results_us_0.img.shape, config_us)
    overlay = draw_curvature(hip_data_us_0, overlay, config_us)

    assert overlay is not None
