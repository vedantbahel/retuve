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

# Assuming get_centering_ratio is defined in the module named `your_module`
from retuve.hip_us.metrics.c_ratio import get_centering_ratio


def test_get_centering_ratio(
    illium_mesh, femoral_sphere, hip_datas_us, config_us, expected_us_metrics
):
    ratio, points = get_centering_ratio(
        illium_mesh, femoral_sphere, hip_datas_us, config_us
    )

    assert isinstance(ratio, float), "Ratio should be a float"
    assert 0 <= ratio <= 1, "Ratio should be between 0 and 1"
    assert len(points) == 3, "Points should contain three elements"
    assert all(
        len(point) == 3 for point in points
    ), "Each point should have three coordinates"

    fem_center, max_z_vert, min_z_vert = points

    assert np.allclose(
        fem_center[2], np.mean(femoral_sphere[2])
    ), "Femoral center z-coordinate should match the mean of femoral sphere z-coordinates"
    assert np.isclose(
        min_z_vert[2], np.min(np.array(illium_mesh.vertices)[:, 2])
    ), "Min z-vertex should match the minimum z-coordinate of the illium mesh"
    assert np.isclose(
        max_z_vert[2], np.max(np.array(illium_mesh.vertices)[:, 2])
    ), "Max z-vertex should match the maximum z-coordinate of the illium mesh"

    assert ratio == expected_us_metrics["centering_ratio"]
