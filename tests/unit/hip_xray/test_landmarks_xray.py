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

from retuve.hip_xray.landmarks import landmarks_2_metrics_xray


def test_landmarks_2_metrics_xray(landmarks_xray_0, config_xray, hip_data_xray_0):
    new_hip = landmarks_2_metrics_xray([landmarks_xray_0], config_xray)

    assert new_hip[0].metrics[0].value == hip_data_xray_0.metrics[0].value
