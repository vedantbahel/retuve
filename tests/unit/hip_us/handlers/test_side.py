import copy
from typing import List

import pytest

from retuve.classes.seg import SegFrameObjects, SegObject
from retuve.hip_us.classes.enums import HipLabelsUS, Side
from retuve.hip_us.classes.general import HipDatasUS, HipDataUS

# Assuming the functions are imported from the module
from retuve.hip_us.handlers.side import get_side_metainfo, set_side


def test_get_side_metainfo(
    hip_data_us_0: HipDataUS, results_us_0: SegFrameObjects
):
    closest_illium, mid = get_side_metainfo(hip_data_us_0, results_us_0)

    assert closest_illium is not None, "Closest illium should not be None"
    assert mid is not None, "Mid point should not be None"
    assert isinstance(
        closest_illium, tuple
    ), "Closest illium should be a tuple"
    assert isinstance(mid, tuple), "Mid point should be a tuple"


def test_set_side_no_landmarks(
    hip_datas_us: HipDatasUS, results_us: List[SegFrameObjects], config_us
):
    hip_datas_us = copy.deepcopy(hip_datas_us)

    # Remove landmarks to test the case where landmarks are None
    for hip_data in hip_datas_us:
        hip_data.landmarks = None
        hip_data.side = None

    updated_hip_datas, updated_results = set_side(
        hip_datas_us, results_us, config_us.hip.allow_flipping
    )

    for hip_data in updated_hip_datas:
        assert (
            hip_data.side is None
        ), "Side should be None when landmarks are missing"


def test_set_side(
    hip_datas_us: HipDatasUS, results_us: List[SegFrameObjects], config_us
):
    updated_hip_datas, updated_results = set_side(
        hip_datas_us, results_us, config_us.hip.allow_flipping
    )

    assert (
        updated_hip_datas is not None
    ), "Updated hip datas should not be None"
    assert updated_results is not None, "Updated results should not be None"

    assert len(updated_hip_datas) == len(
        hip_datas_us
    ), "Length of hip datas should be unchanged"
    assert len(updated_results) == len(
        results_us
    ), "Length of results should be unchanged"

    front_count = sum(
        1 for hip_data in updated_hip_datas if hip_data.side == Side.ANT
    )
    back_count = sum(
        1 for hip_data in updated_hip_datas if hip_data.side == Side.POST
    )

    assert (
        front_count > 0
    ), "There should be some frames classified as front (ANT)"
    assert (
        back_count > 0
    ), "There should be some frames classified as back (POST)"


def test_set_side_error_handling(
    hip_datas_us: HipDatasUS, results_us: List[SegFrameObjects], config_us
):
    # Manipulate hip_datas to create a condition where no front side is detected
    hip_datas_us.graf_frame = 0  # Ensuring no front side frames

    updated_hip_datas, updated_results = set_side(
        hip_datas_us, results_us, config_us.hip.allow_flipping
    )

    assert (
        "No Front Side." in updated_hip_datas.recorded_error.errors
    ), "Error 'No Front Side.' should be recorded"
    assert (
        updated_hip_datas.recorded_error.critical
    ), "Recorded error should be marked as critical"


@pytest.fixture
def manipulated_hip_datas(hip_datas_us):
    # Function to manipulate hip_datas for specific test cases
    hip_datas_us.graf_frame = 5  # Set a graf frame to split sides

    for i, hip_data in enumerate(hip_datas_us):
        hip_data.frame_no = i
        if not hip_data.marked():
            continue
        if i < 5:
            hip_data.landmarks.apex = (10, 20)  # Dummy values for landmarks
        else:
            hip_data.landmarks.apex = (30, 40)
    return hip_datas_us


def test_set_side_swap_post_ant(
    manipulated_hip_datas: HipDatasUS,
    results_us: List[SegFrameObjects],
    config_us,
):
    updated_hip_datas, updated_results = set_side(
        manipulated_hip_datas, results_us, config_us.hip.allow_flipping
    )

    assert (
        "Swapped Post and Ant" in updated_hip_datas.recorded_error.errors
    ), "Error 'Swapped Post and Ant' should be recorded"
    assert (
        updated_hip_datas.hip_datas != manipulated_hip_datas
    ), "Hip datas should have been reversed"
    assert updated_results != results_us, "Results should have been reversed"
