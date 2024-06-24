import pydicom
from PIL import Image
from radstract.data.dicom import convert_dicom_to_images

from retuve.defaults.hip_configs import default_US, default_xray
from retuve.defaults.manual_seg import (
    manual_predict_us,
    manual_predict_us_dcm,
    manual_predict_xray,
)
from retuve.funcs import (
    analyse_hip_2DUS,
    analyse_hip_2DUS_sweep,
    analyse_hip_3DUS,
    analyse_hip_xray_2D,
    retuve_run,
)
from retuve.keyphrases.enums import HipMode

metrics_3d_us = {
    "metrics": [
        {"Aca": [70.09, 61.62, 58.38, 63.36]},
        {"Cen. ratio": ["N/A", "N/A", "N/A", 0.55]},
        {"Alpha": [68.43, 75.6, 70.18, 71.4]},
        {"Coverage": [0.62, 0.72, 0.64, 0.66]},
        {"Curvature": [1.67, 1.4, 1.66, 1.58]},
    ],
    "graf_frame": 7,
    "dev_metrics": {
        "os_ichium_detected": True,
        "no_frames_segmented": 15,
        "no_frames_marked": 10,
        "graf_frame": 7,
        "acetabular_mid_frame": 8,
        "fem_mid_frame": 7,
        "critial_error": False,
        "cr_points": [3.0, 14.0, 8.0],
        "total_frames": 15,
    },
    "recorded_error": "Swapped Post and Ant ",
    "keyphrase": "default_US",
}

metrics_xray = {
    "metrics": [{"ace_index_left": 27.3}, {"ace_index_right": 19.7}],
    "keyphrase": "default_xray",
    "dev_metrics": {},
}

metrics_2d_sweep = {
    "metrics": [{"alpha": 75.6}, {"coverage": 0.72}, {"curvature": 1.4}],
    "keyphrase": "default_US",
    "dev_metrics": {
        "os_ichium_detected": True,
        "no_frames_segmented": 15,
        "no_frames_marked": 10,
        "graf_frame": 8,
        "acetabular_mid_frame": 8,
        "fem_mid_frame": 7,
        "critial_error": False,
        "cr_points": [],
        "total_frames": 15,
    },
}

metrics_2d_us = {
    "metrics": [{"alpha": 66.4}, {"coverage": 0.612}, {"curvature": 1.76}],
    "keyphrase": "default_US",
    "dev_metrics": {
        "os_ichium_detected": True,
        "no_frames_segmented": 1,
        "no_frames_marked": 1,
        "graf_frame": None,
        "acetabular_mid_frame": 0,
        "fem_mid_frame": 0,
        "critial_error": False,
        "cr_points": [],
        "total_frames": 1,
    },
}


def test_analyse_hip_3DUS(us_file_path):
    seg_file = us_file_path.replace(".dcm", ".nii.gz")

    dcm = pydicom.dcmread(us_file_path)

    hip_datas, *_ = analyse_hip_3DUS(
        dcm,
        keyphrase=default_US,
        modes_func=manual_predict_us_dcm,
        modes_func_kwargs_dict={"seg": seg_file},
    )

    metrics = hip_datas.json_dump(default_US)

    assert metrics == metrics_3d_us


def test_retuve_run_3DUS(us_file_path):
    seg_file = us_file_path.replace(".dcm", ".nii.gz")

    retuve_result = retuve_run(
        hip_mode=HipMode.US3D,
        config=default_US,
        modes_func=manual_predict_us_dcm,
        modes_func_kwargs_dict={"seg": seg_file},
        file=us_file_path,
    )

    assert retuve_result.metrics == metrics_3d_us


def test_analyse_hip_xray_2D(landmarks_xray, xray_file_path):
    img = Image.open(xray_file_path)

    hip_data, img, dev_metrics = analyse_hip_xray_2D(
        img,
        keyphrase=default_xray,
        modes_func=manual_predict_xray,
        modes_func_kwargs_dict={"landmark_list": [landmarks_xray]},
    )

    metrics = hip_data.json_dump(default_xray, dev_metrics)

    assert metrics == metrics_xray


def test_retuve_run_xray(landmarks_xray, xray_file_path):

    retuve_result = retuve_run(
        hip_mode=HipMode.XRAY,
        config=default_xray,
        modes_func=manual_predict_xray,
        modes_func_kwargs_dict={"landmark_list": [landmarks_xray]},
        file=xray_file_path,
    )

    assert retuve_result.metrics == metrics_xray


def test_analyse_hip_2DUS(us_file_path):

    seg_file = us_file_path.replace(".dcm", ".nii.gz")
    dcm = pydicom.dcmread(us_file_path)

    images = convert_dicom_to_images(dcm)

    hip_data, _, dev_metrics = analyse_hip_2DUS(
        images[0],
        keyphrase=default_US,
        modes_func=manual_predict_us,
        modes_func_kwargs_dict={"seg": seg_file},
    )

    metrics = hip_data.json_dump(default_US, dev_metrics)

    assert metrics == metrics_2d_us


def test_analyse_hip_2DUS_sweep(us_file_path):

    seg_file = us_file_path.replace(".dcm", ".nii.gz")
    dcm = pydicom.dcmread(us_file_path)

    hip_data, _, dev_metrics, _ = analyse_hip_2DUS_sweep(
        dcm,
        keyphrase=default_US,
        modes_func=manual_predict_us_dcm,
        modes_func_kwargs_dict={"seg": seg_file},
    )

    metrics = hip_data.json_dump(default_US, dev_metrics)

    assert metrics == metrics_2d_sweep
