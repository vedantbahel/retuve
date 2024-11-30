import copy

import pytest
from sklearn import metrics

from retuve.hip_us.classes.general import HipDatasUS


@pytest.fixture
def expected_xray_metrics(metrics_xray):

    metrics = {}
    for _dict in metrics_xray["metrics"]:
        metrics.update(_dict)

    return {
        "ace_left": metrics["ace_index_left"],
        "ace_right": metrics["ace_index_right"],
    }


@pytest.fixture
def expected_us_metrics(metrics_3d_us, metrics_2d_us):

    # metrics_3d_us["metrics"] is wrapped in lists for each key
    # i.e metrics_3d_us["metrics"][0]["Cen. ratio"], metrics_3d_us["metrics"][1]["Aca"]
    # please undo this wrapping before using the metrics
    metrics_3dus = {}
    for _dict in metrics_3d_us["metrics"]:
        metrics_3dus.update(_dict)

    # same for metrics_2d_us
    metrics_2dus = {}
    for _dict in metrics_2d_us["metrics"]:
        metrics_2dus.update(_dict)

    return {
        "centering_ratio": metrics_3dus["Cen. ratio"][3],
        "curvature": metrics_2dus["curvature"],
        "alpha": metrics_2dus["alpha"],
        "aca_post": metrics_3dus["Aca"][0],
        "aca_ant": metrics_3dus["Aca"][2],
        "aca_graf": metrics_3dus["Aca"][1],
        # Hack since we don't run the thirds pipeline
        "aca_thirds_range": range(55, 70),
        "outliers": [
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
        ],
        "frame_with_results": 4,
        "frame_with_no_results": 0,
        "flipped": False,
    }


@pytest.fixture
def edited_hips(pre_edited_hip_datas_us: HipDatasUS):
    hip_datas_us = copy.deepcopy(pre_edited_hip_datas_us)

    return hip_datas_us
