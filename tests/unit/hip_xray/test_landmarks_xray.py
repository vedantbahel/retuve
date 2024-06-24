from retuve.hip_xray.landmarks import landmarks_2_metrics_xray


def test_landmarks_2_metrics_xray(
    landmarks_xray_0, config_xray, hip_data_xray_0
):
    new_hip = landmarks_2_metrics_xray([landmarks_xray_0], config_xray)

    assert new_hip[0].metrics[0].value == hip_data_xray_0.metrics[0].value
