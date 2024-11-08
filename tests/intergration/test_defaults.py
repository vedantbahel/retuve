import pytest

from retuve.defaults.manual_seg import manual_predict_us, manual_predict_us_dcm
from retuve.hip_us.classes.enums import HipLabelsUS

XRAY_FILE_PATH = "./tests/test-data/224_DDH_115.jpg"
US_FILE_PATH = "./tests/test-data/171551.dcm"
US_NII_FILE_PATH = "./tests/test-data/171551.nii.gz"


def test_manual_predict_us_dcm(
    us_dcm, config_us, results_us, us_nii_file_path, us_full_result_info
):
    new_results = manual_predict_us_dcm(
        us_dcm, config_us, seg=us_nii_file_path
    )
    if us_full_result_info.FLIPPED:
        new_results = new_results[::-1]
    illium = [
        x
        for x in results_us[us_full_result_info.FRAME]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ][0]
    new_illium = [
        x
        for x in new_results[us_full_result_info.FRAME]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ][0]

    assert illium.points == new_illium.points


def test_manual_predict_us(
    us_images, config_us, us_nii_file_path, results_us, us_full_result_info
):
    new_results = manual_predict_us(us_images, config_us, seg=us_nii_file_path)
    if us_full_result_info.FLIPPED:
        new_results = new_results[::-1]
    assert results_us is not None
    illium = [
        x
        for x in results_us[us_full_result_info.FRAME]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ]
    illium = illium[0]
    new_illium = [
        x
        for x in new_results[us_full_result_info.FRAME]
        if x.cls == HipLabelsUS.IlliumAndAcetabulum
    ][0]

    assert illium.points == new_illium.points


def test_manual_predict_us_raises_value_error(us_images, config_us):
    with pytest.raises(ValueError):
        manual_predict_us(us_images, config_us)
