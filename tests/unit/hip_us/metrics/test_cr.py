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
