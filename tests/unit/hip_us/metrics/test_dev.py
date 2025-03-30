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

import copy

from retuve.hip_us.classes.general import HipDatasUS
from retuve.hip_us.metrics.dev import get_dev_metrics


def test_get_dev_metrics_execution(hip_datas_us, results_us, config_us):
    """
    Test if the get_dev_metrics function executes successfully.
    """
    hip_datas_before = copy.deepcopy(hip_datas_us)
    hip_datas_us.dev_metrics = None

    hip_datas_us = get_dev_metrics(hip_datas_us, results_us, config_us)
    assert isinstance(hip_datas_us, HipDatasUS)

    assert (
        hip_datas_before.dev_metrics.os_ichium_detected
        == hip_datas_us.dev_metrics.os_ichium_detected
    )
    assert (
        hip_datas_before.dev_metrics.no_frames_segmented
        == hip_datas_us.dev_metrics.no_frames_segmented
    )
    assert (
        hip_datas_before.dev_metrics.no_frames_marked
        == hip_datas_us.dev_metrics.no_frames_marked
    )
    assert (
        hip_datas_before.dev_metrics.graf_frame == hip_datas_us.dev_metrics.graf_frame
    )
    assert (
        hip_datas_before.dev_metrics.acetabular_mid_frame
        == hip_datas_us.dev_metrics.acetabular_mid_frame
    )
    assert (
        hip_datas_before.dev_metrics.fem_mid_frame
        == hip_datas_us.dev_metrics.fem_mid_frame
    )
    assert (
        hip_datas_before.dev_metrics.critial_error
        == hip_datas_us.dev_metrics.critial_error
    )
    assert hip_datas_before.dev_metrics.cr_points == hip_datas_us.dev_metrics.cr_points
    assert (
        hip_datas_before.dev_metrics.total_frames
        == hip_datas_us.dev_metrics.total_frames
    )
