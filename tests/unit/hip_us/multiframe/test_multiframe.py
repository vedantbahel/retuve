import numpy as np

from retuve.hip_us.multiframe import (
    find_graf_plane,
    get_3d_metrics_and_visuals,
)


def test_get_3d_metrics_and_visuals_success(
    hip_datas_us,
    results_us,
    config_us,
    femoral_sphere,
):
    (
        new_hip_datas,
        visual_3d,
        new_fem_sph,
        new_illium_mesh,
        _,
        new_femoral_sphere,
        avg_normals_data,
        normals_data,
    ) = get_3d_metrics_and_visuals(
        hip_datas_us,
        results_us,
        config_us,
    )

    assert new_illium_mesh is not None, "Illium mesh should not be None"
    assert new_femoral_sphere is not None, "Femoral sphere should not be None"
    assert visual_3d is not None, "3D visual should not be None"
    assert (
        len(hip_datas_us.metrics) > 0
    ), "Metrics should be computed and added to hip_datas"
    assert new_fem_sph is not None, "FemSphere should not be None"

    # check that the hip_datas metrics are the same as the old ones
    for i, hip_data in enumerate(hip_datas_us):
        assert (
            hip_data.metrics == new_hip_datas[i].metrics
        ), "Metrics should be the same"

    assert np.array_equal(
        new_femoral_sphere, femoral_sphere
    ), "Femoral sphere should be the same"


def test_find_graf_plane_success(
    hip_datas_us,
):
    hip_datas_us.graf_frame = None
    hip_datas_us.grafs_hip = None

    hip_datas_us = find_graf_plane(hip_datas_us)
    assert (
        hip_datas_us.graf_frame is not None
    ), "Graf frame should be identified"
    assert hip_datas_us.grafs_hip is not None, "Grafs hip should be identified"


def test_find_graf_plane_no_good_graf_frames(
    hip_datas_us,
):
    for hip_data in hip_datas_us:
        hip_data.metrics = []  # Simulate no good graf frames

    hip_datas_us = find_graf_plane(hip_datas_us)
    assert (
        hip_datas_us.graf_frame is not None
    ), "Graf frame should still be identified even if no good graf frames"
    assert (
        "No Perfect Grafs Frames found." in hip_datas_us.recorded_error.errors
    ), "Error should be recorded for no good graf frames"
