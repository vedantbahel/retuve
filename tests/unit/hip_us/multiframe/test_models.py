import math

import numpy as np
import pytest

from retuve.hip_us.multiframe.models import (
    build_3d_visual,
    circle_radius_at_z,
    get_femoral_sphere,
    get_illium_mesh,
)


def test_get_femoral_sphere(hip_datas_us, config_us, femoral_sphere):
    new_femoral_sphere, radius = get_femoral_sphere(hip_datas_us, config_us)
    assert new_femoral_sphere is not None
    assert radius > 0
    assert np.array_equal(
        new_femoral_sphere, femoral_sphere
    ), "Femoral sphere should be the same"


def test_get_illium_mesh(hip_datas_us, illium_mesh, results_us, config_us):
    illium_mesh_new, apex_points = get_illium_mesh(
        hip_datas_us, results_us, config_us
    )
    assert illium_mesh_new is not None
    assert len(apex_points) > 0
    assert (
        np.array(illium_mesh_new.vertices).shape
        == np.array(illium_mesh.vertices).shape
    )


def test_build_3d_visual(
    illium_mesh,
    femoral_sphere,
    avg_normals_data,
    normals_data,
    hip_datas_us,
    config_us,
):
    cr_points = [[1, 3, 7]]
    fig = build_3d_visual(
        illium_mesh,
        femoral_sphere,
        avg_normals_data,
        normals_data,
        cr_points,
        hip_datas_us,
        config_us,
    )
    assert fig is not None
    assert len(fig.data) > 0


@pytest.mark.parametrize(
    "sphere_radius, z_center, z_input, expected",
    [
        (10, 5, 5, 10),  # At center of sphere
        (10, 5, 0, 8.66),  # Below center, inside sphere
        (10, 5, 10, 8.66),  # Above center, inside sphere
        (10, 5, 15, 0),  # Above center, outside sphere
        (10, 5, -5, 0),  # Below center, outside sphere
        (5, 0, 3, 4),  # Center at origin, input inside sphere
        (5, 0, 5, 0),  # Center at origin, input at sphere boundary
    ],
)
def test_circle_radius_at_z(sphere_radius, z_center, z_input, expected):
    radius = circle_radius_at_z(sphere_radius, z_center, z_input)
    assert math.isclose(radius, expected, rel_tol=1e-3)
