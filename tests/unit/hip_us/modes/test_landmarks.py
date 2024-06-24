import time
from typing import List

from retuve.classes.seg import SegFrameObjects
from retuve.hip_us.classes.general import HipDatasUS, LandmarksUS
from retuve.hip_us.modes.landmarks import landmarks_2_metrics_us
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import MetricUS


def test_landmarks_2_metrics_us(
    landmarks_us: List[LandmarksUS],
    hip_datas_us: HipDatasUS,
    results_us_0: SegFrameObjects,
    config_us: Config,
):
    shape = results_us_0.img.shape
    hips = landmarks_2_metrics_us(landmarks_us, shape, config_us)

    # remove any old or new hips with no landmarks
    hips = [hip for hip in hips if hip.landmarks]
    hip_datas_us = [hip for hip in hip_datas_us if hip.landmarks]

    for new_hip, old_hip in zip(hips, hip_datas_us):
        assert new_hip.frame_no == old_hip.frame_no
        assert new_hip.get_metric(MetricUS.COVERAGE) == old_hip.get_metric(
            MetricUS.COVERAGE
        )
        assert new_hip.get_metric(MetricUS.ALPHA) == old_hip.get_metric(
            MetricUS.ALPHA
        )
        assert new_hip.get_metric(MetricUS.CURVATURE) == old_hip.get_metric(
            MetricUS.CURVATURE
        )
        # remove any old or new landmarks that are None
        old_hip.landmarks = [
            landmark for landmark in old_hip.landmarks if landmark is not None
        ]

        new_hip.landmarks = [
            landmark for landmark in new_hip.landmarks if landmark is not None
        ]
        assert all(
            [
                old_landmark == new_landmark
                for old_landmark, new_landmark in zip(
                    old_hip.landmarks, new_hip.landmarks
                )
            ]
        )
