import copy

import pytest

from retuve.classes.metrics import Metric2D
from retuve.hip_us.classes.general import HipDatasUS
from retuve.keyphrases.enums import MetricUS


@pytest.fixture
def expected_xray_metrics():
    return {
        "ace_left": 24.2,
        "ace_right": 28.2,
    }


@pytest.fixture
def expected_us_metrics():
    return {
        "centering_ratio": 0.55,
        "curvature": 1.75,
        "alpha": 65.6,
        "landmark_left": (171, 378),
        "landmark_right": (463, 525),
        "landmark_apex": (371, 361),
        "aca_post": 70.09,
        "aca_ant": 58.38,
        "aca_graf": 61.62,
        "aca_post_thirds": 61.9,
        "aca_ant_thirds": 57.34,
        "aca_graf_thirds": 59.9,
        "first_avg_normal": [0.03, -0.9, -0.41],
        "second_avg_normal": [0.06, -0.9, 0.14],
        "first_avg_normal_thirds": [0.03, -0.91, -0.27],
        "second_avg_normal_thirds": [0.07, -0.89, 0.2],
        "outliers": [
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
        ],
        "frame_with_results": 0,
        "frame_with_no_results": 3,
    }


@pytest.fixture
def edited_hips(pre_edited_hip_datas_us: HipDatasUS):
    hip_datas_us = copy.deepcopy(pre_edited_hip_datas_us)

    return hip_datas_us
