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
        hip_datas_before.dev_metrics.graf_frame
        == hip_datas_us.dev_metrics.graf_frame
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
    assert (
        hip_datas_before.dev_metrics.cr_points
        == hip_datas_us.dev_metrics.cr_points
    )
    assert (
        hip_datas_before.dev_metrics.total_frames
        == hip_datas_us.dev_metrics.total_frames
    )
