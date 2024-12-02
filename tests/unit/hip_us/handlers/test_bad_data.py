from cv2 import exp

from retuve.hip_us.handlers.bad_data import handle_bad_frames, remove_outliers


def test_remove_outliers(edited_hips, expected_us_metrics):
    # Create some sample data
    config = {}  # Sample config

    keep = remove_outliers(edited_hips, config)

    # Validate the result
    assert (
        keep == expected_us_metrics["outliers"]
    ), f"Outliers not removed correctly {keep}"


def test_handle_bad_frames(edited_hips, expected_us_metrics, config_us):

    result = handle_bad_frames(edited_hips, config_us)

    idx_results = expected_us_metrics["frame_with_results"]
    idx_no_results = expected_us_metrics["frame_with_no_results"]

    # Validate the result
    assert (
        result[idx_no_results].frame_no == idx_no_results
        and result[idx_no_results].metrics is None
    )
    assert (
        result[idx_results].frame_no == idx_results
        and result[idx_results].metrics is not None
    )
