import numpy as np
import pytest

from retuve.hip_us.classes.enums import Side
from retuve.hip_us.metrics.aca import ACA_COLORS, SideZ, Triangle, get_aca
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import ACASplit


def test_triangle_initialization():
    apex_side = SideZ.LEFT
    third = Side.POST
    normal = np.array([0, 0, 1])
    centroid = np.array([1, 2, 3])
    triangle = Triangle(apex_side, third, normal, centroid)

    assert triangle.apex_side == apex_side
    assert triangle.third == third
    assert np.array_equal(triangle.normal, normal)
    assert np.array_equal(triangle.centroid, centroid)
    assert triangle.color == ACA_COLORS[(apex_side, third)]


def test_get_aca_thirds(
    illium_mesh, apex_points, hip_datas_us, config_us, expected_us_metrics
):
    config_us.hip.aca_split = ACASplit.THIRDS
    no_of_frames = len(hip_datas_us)

    aca_angles, avg_normals_data, triangle_data, recorded_error = get_aca(
        illium_mesh,
        apex_points,
        hip_datas_us.grafs_hip,
        no_of_frames,
        config_us,
    )

    # Since we do not run the thirds pipeline, just check
    # that the angles are within the expected range
    assert int(aca_angles[Side.ANT]) in expected_us_metrics["aca_thirds_range"]
    assert (
        int(aca_angles[Side.POST]) in expected_us_metrics["aca_thirds_range"]
    )
    assert (
        int(aca_angles[Side.GRAF]) in expected_us_metrics["aca_thirds_range"]
    )

    assert recorded_error == ""


def test_get_aca_grafs(
    illium_mesh, apex_points, hip_datas_us, config_us, expected_us_metrics
):
    config_us.hip.aca_split = ACASplit.GRAFS
    no_of_frames = len(hip_datas_us)

    aca_angles, avg_normals_data, triangle_data, recorded_error = get_aca(
        illium_mesh,
        apex_points,
        hip_datas_us.grafs_hip,
        no_of_frames,
        config_us,
    )

    assert aca_angles == {
        Side.ANT: expected_us_metrics["aca_ant"],
        Side.POST: expected_us_metrics["aca_post"],
        Side.GRAF: expected_us_metrics["aca_graf"],
    }

    assert recorded_error == ""
