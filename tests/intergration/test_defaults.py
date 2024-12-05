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

from retuve.defaults.manual_seg import manual_predict_us, manual_predict_us_dcm
from retuve.hip_us.classes.enums import HipLabelsUS

XRAY_FILE_PATH = "./tests/test-data/331_DDH_115.jpg"
US_FILE_PATH = "./tests/test-data/171551.dcm"
US_NII_FILE_PATH = "./tests/test-data/171551.nii.gz"


def test_manual_predict_us_dcm(
    us_dcm, config_us, results_us, us_nii_file_path, expected_us_metrics
):
    new_results = manual_predict_us_dcm(
        us_dcm, config_us, seg=us_nii_file_path
    )
    if expected_us_metrics["flipped"]:
        new_results = new_results[::-1]
    illium = [
        x
        for x in results_us[expected_us_metrics["frame_with_results"]]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ][0]
    new_illium = [
        x
        for x in new_results[expected_us_metrics["frame_with_results"]]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ][0]

    assert illium.points == new_illium.points


def test_manual_predict_us(
    us_images, config_us, us_nii_file_path, results_us, expected_us_metrics
):
    new_results = manual_predict_us(us_images, config_us, seg=us_nii_file_path)
    if expected_us_metrics["flipped"]:
        new_results = new_results[::-1]
    assert results_us is not None
    illium = [
        x
        for x in results_us[expected_us_metrics["frame_with_results"]]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ]
    illium = illium[0]
    new_illium = [
        x
        for x in new_results[expected_us_metrics["frame_with_results"]]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ][0]

    assert illium.points == new_illium.points


def test_manual_predict_us_raises_value_error(us_images, config_us):
    with pytest.raises(ValueError):
        manual_predict_us(us_images, config_us)
