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

from cv2 import exp

from retuve.hip_us.handlers.bad_data import handle_bad_frames, remove_outliers


def test_remove_outliers(edited_hips, expected_us_metrics):
    # Create some sample data
    config = {}  # Sample config

    keep = remove_outliers(edited_hips, config)

    # Validate the result
    assert (
        keep == expected_us_metrics["outliers"]
    ), f"Outliers not removed correctly {keep}"


def test_handle_bad_frames(edited_hips, expected_us_metrics, config_us):

    result = handle_bad_frames(edited_hips, config_us)

    idx_results = expected_us_metrics["frame_with_results"]
    idx_no_results = expected_us_metrics["frame_with_no_results"]

    # Validate the result
    assert (
        result[idx_no_results].frame_no == idx_no_results
        and result[idx_no_results].metrics is None
    )
    assert (
        result[idx_results].frame_no == idx_results
        and result[idx_results].metrics is not None
    )
