"""
Contains the high-level functions that are used to run the Retuve pipeline.
"""

import copy
from typing import Any, BinaryIO, Callable, Dict, List, Tuple, Union

import pydicom
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from PIL import Image
from plotly.graph_objs import Figure
from radstract.data.dicom import convert_dicom_to_images
from radstract.data.nifti import NIFTI, convert_images_to_nifti_labels

from retuve.classes.draw import Overlay
from retuve.classes.metrics import Metric2D, Metric3D
from retuve.classes.seg import SegFrameObjects
from retuve.hip_us.classes.dev import DevMetricsUS
from retuve.hip_us.classes.general import HipDatasUS, HipDataUS
from retuve.hip_us.draw import draw_hips_us, draw_table
from retuve.hip_us.handlers.bad_data import handle_bad_frames
from retuve.hip_us.handlers.side import set_side
from retuve.hip_us.metrics.dev import get_dev_metrics
from retuve.hip_us.modes.landmarks import landmarks_2_metrics_us
from retuve.hip_us.modes.seg import pre_process_segs_us, segs_2_landmarks_us
from retuve.hip_us.multiframe import (find_graf_plane,
                                      get_3d_metrics_and_visuals)
from retuve.hip_xray.classes import DevMetricsXRay, HipDataXray, LandmarksXRay
from retuve.hip_xray.draw import draw_hips_xray
from retuve.hip_xray.landmarks import landmarks_2_metrics_xray
from retuve.keyphrases.config import Config, OperationType
from retuve.keyphrases.enums import HipMode
from retuve.typehints import GeneralModeFuncType


def process_landmarks_xray(
    config: Config,
    landmark_results: List[LandmarksXRay],
    seg_results: List[SegFrameObjects],
) -> Tuple[List[HipDataXray], List[Image.Image]]:
    """
    Process the landmarks for the xray.

    :param config: The configuration.
    :param landmark_results: The landmark results.
    :param seg_results: The segmentation results.

    :return: The hip datas and the image arrays.
    """
    img = seg_results[0].img
    hip_datas_xray = landmarks_2_metrics_xray(landmark_results, config)
    image_arrays = draw_hips_xray(
        hip_datas_xray, seg_results, img.shape, config
    )
    return hip_datas_xray, image_arrays


def process_segs_us(
    config: Config,
    file: BinaryIO,
    modes_func: Callable[
        [BinaryIO, Union[str, Config], Dict[str, Any]],
        List[SegFrameObjects],
    ],
    modes_func_kwargs_dict: Dict[str, Any],
) -> Tuple[HipDatasUS, List[SegFrameObjects], Tuple[int, int, int]]:
    """
    Process the segmentation for the 3DUS.

    :param config: The configuration.
    :param file: The file.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.

    :return: The hip datas, the results, and the shape.
    """

    results: List[SegFrameObjects] = modes_func(
        file, config, **modes_func_kwargs_dict
    )
    results, shape = pre_process_segs_us(results, config)
    pre_edited_results = copy.deepcopy(results)
    landmarks = segs_2_landmarks_us(results, config)
    pre_edited_landmarks = copy.deepcopy(landmarks)
    hip_datas = landmarks_2_metrics_us(landmarks, shape, config)

    if config.test_data_passthrough:
        hip_datas.pre_edited_results = pre_edited_results
        hip_datas.pre_edited_landmarks = pre_edited_landmarks
        hip_datas.pre_edited_hip_datas = copy.deepcopy(hip_datas)

    return hip_datas, results, shape


def analyse_hip_xray_2D(
    img: Image.Image,
    keyphrase: Union[str, Config],
    modes_func: Callable[
        [Image.Image, str, Dict[str, Any]],
        Tuple[List[LandmarksXRay], List[SegFrameObjects]],
    ],
    modes_func_kwargs_dict: Dict[str, Any],
) -> Tuple[HipDataXray, Image.Image, DevMetricsXRay]:
    """
    Analyze the hip for the xray.

    :param img: The image.
    :param keyphrase: The keyphrase.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.

    :return: The hip, the image, and the dev metrics.
    """
    if isinstance(keyphrase, str):
        config = Config.get_config(keyphrase)
    else:
        config = keyphrase

    if config.operation_type in OperationType.LANDMARK:
        landmark_results, seg_results = modes_func(
            [img], keyphrase, **modes_func_kwargs_dict
        )
        hip_datas, image_arrays = process_landmarks_xray(
            config, landmark_results, seg_results
        )

    img = image_arrays[0]
    img = Image.fromarray(img)
    hip = hip_datas[0]

    if config.test_data_passthrough:
        hip.seg_results = seg_results

    return hip, img, DevMetricsXRay()


def analyze_synthetic_xray(
    dcm: pydicom.FileDataset,
    keyphrase: Union[str, Config],
    modes_func: Callable[
        [pydicom.FileDataset, str, Dict[str, Any]],
        Tuple[List[LandmarksXRay], List[SegFrameObjects]],
    ],
    modes_func_kwargs_dict: Dict[str, Any],
) -> NIFTI:
    """
    NOTE: Experimental function.

    Useful if the xray images are stacked in a single DICOM file.

    Analyze the hip for the xray.

    :param dcm: The DICOM file.
    :param keyphrase: The keyphrase.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.

    :return: The nifti segmentation file
    """
    if isinstance(keyphrase, str):
        config = Config.get_config(keyphrase)
    else:
        config = keyphrase

    images = convert_dicom_to_images(dcm)

    if config.operation_type in OperationType.LANDMARK:
        landmark_results, seg_results = modes_func(
            images, keyphrase, **modes_func_kwargs_dict
        )
        hip_datas, image_arrays = process_landmarks_xray(
            config, landmark_results, seg_results
        )

    nifti_frames = []
    for hip, seg_frame_objs in zip(hip_datas, seg_results):
        shape = seg_frame_objs.img.shape

        overlay = Overlay((shape[0], shape[1], 3), config)
        test = overlay.get_nifti_frame(seg_frame_objs)
        nifti_frames.append(test)

    # convert to nifti
    nifti = convert_images_to_nifti_labels(nifti_frames)

    return nifti


def analyse_hip_3DUS(
    dcm: pydicom.FileDataset,
    keyphrase: Union[str, Config],
    modes_func: Callable[
        [pydicom.FileDataset, str, Dict[str, Any]],
        List[SegFrameObjects],
    ],
    modes_func_kwargs_dict: Dict[str, Any],
) -> Tuple[
    HipDatasUS,
    ImageSequenceClip,
    Figure,
    Union[DevMetricsXRay, DevMetricsUS],
]:
    """
    Analyze a 3D Ultrasound Hip

    :param dcm: The DICOM file.
    :param keyphrase: The keyphrase.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.

    :return: The hip datas, the video clip, the 3D visual, and the dev metrics.
    """
    config = Config.get_config(keyphrase)
    hip_datas = HipDatasUS()

    if config.operation_type == OperationType.SEG:
        hip_datas, results, shape = process_segs_us(
            config, dcm, modes_func, modes_func_kwargs_dict
        )
    elif config.operation_type == OperationType.LANDMARK:
        raise NotImplementedError(
            "This is not yet supported. Please use the seg operation type."
        )

    hip_datas = handle_bad_frames(hip_datas, config)

    if not any(hip.metrics for hip in hip_datas):
        raise ValueError("No hip was found in the DICOM.")

    hip_datas = find_graf_plane(hip_datas)

    if config.hip.allow_flipping:
        hip_datas, results = set_side(hip_datas, results)

    (
        hip_datas,
        visual_3d,
        fem_sph,
        illium_mesh,
        apex_points,
        femoral_sphere,
        avg_normals_data,
        normals_data,
    ) = get_3d_metrics_and_visuals(hip_datas, results, config)

    image_arrays, nifti = draw_hips_us(
        hip_datas, results, shape, fem_sph, config
    )

    if config.seg_export:
        hip_datas.nifti = nifti

    hip_datas = get_dev_metrics(hip_datas, results, config)

    data_image = draw_table(shape, hip_datas)
    image_arrays.append(data_image)

    video_clip = ImageSequenceClip(image_arrays, fps=len(image_arrays) / 4)

    if config.test_data_passthrough:
        hip_datas.illium_mesh = illium_mesh
        hip_datas.fem_sph = fem_sph
        hip_datas.results = results
        hip_datas.apex_points = apex_points
        hip_datas.femoral_sphere = femoral_sphere
        hip_datas.avg_normals_data = avg_normals_data
        hip_datas.normals_data = normals_data

    return (
        hip_datas,
        video_clip,
        visual_3d,
        hip_datas.dev_metrics,
    )


def analyse_hip_2DUS(
    img: Image.Image,
    keyphrase: Union[str, Config],
    modes_func: Callable[
        [Image.Image, str, Dict[str, Any]],
        List[SegFrameObjects],
    ],
    modes_func_kwargs_dict: Dict[str, Any],
) -> Tuple[HipDataUS, Image.Image, DevMetricsUS]:
    """
    Analyze a 2D Ultrasound Hip

    :param img: The image.
    :param keyphrase: The keyphrase.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.

    :return: The hip, the image, and the dev metrics.
    """
    config = Config.get_config(keyphrase)

    if config.operation_type in OperationType.SEG:
        hip_datas, results, shape = process_segs_us(
            config, [img], modes_func, modes_func_kwargs_dict
        )

    image_arrays, _ = draw_hips_us(hip_datas, results, shape, None, config)

    hip_datas = get_dev_metrics(hip_datas, results, config)

    image = image_arrays[0]
    hip = hip_datas[0]

    image = Image.fromarray(image)

    return hip, image, hip_datas.dev_metrics


def analyse_hip_2DUS_sweep(
    dcm: pydicom.FileDataset,
    keyphrase: Union[str, Config],
    modes_func: Callable[
        [pydicom.FileDataset, str, Dict[str, Any]],
        List[SegFrameObjects],
    ],
    modes_func_kwargs_dict: Dict[str, Any],
) -> Tuple[
    HipDatasUS,
    Image.Image,
    DevMetricsUS,
    ImageSequenceClip,
]:
    """
    Analyze a 2D Sweep Ultrasound Hip

    :param dcm: The DICOM file.
    :param keyphrase: The keyphrase.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.

    :return: The hip, the image, the dev metrics, and the video clip.
    """

    config = Config.get_config(keyphrase)
    hip_datas = HipDatasUS()

    if config.operation_type == OperationType.SEG:
        hip_datas, results, shape = process_segs_us(
            config, dcm, modes_func, modes_func_kwargs_dict
        )
    elif config.operation_type == OperationType.LANDMARK:
        raise NotImplementedError(
            "This is not yet supported. Please use the seg operation type."
        )

    hip_datas = handle_bad_frames(hip_datas, config)
    hip_datas = find_graf_plane(hip_datas)

    hip = hip_datas.grafs_hip
    frame = hip_datas.graf_frame

    image_arrays, _ = draw_hips_us(hip_datas, results, shape, None, config)

    hip_datas = get_dev_metrics(hip_datas, results, config)

    image = image_arrays[frame]
    hip = hip_datas[frame]

    image = Image.fromarray(image)

    video_clip = ImageSequenceClip(image_arrays, fps=len(image_arrays) / 4)

    return hip, image, hip_datas.dev_metrics, video_clip


class RetuveResult:
    """
    The standardised result of the Retuve pipeline.

    :attr hip_datas: The hip datas.
    :attr hip: The hip.
    :attr image: The saved image, if any.
    :attr metrics: The metrics.
    :attr video_clip: The video clip, if any.
    :attr visual_3d: The 3D visual, if any.
    """

    def __init__(
        self,
        metrics: Union[List[Metric2D], List[Metric3D]],
        hip_datas: Union[HipDatasUS, List[HipDataXray]] = None,
        hip: Union[HipDataXray, HipDataUS] = None,
        image: Image.Image = None,
        video_clip: ImageSequenceClip = None,
        visual_3d: Figure = None,
    ):
        self.hip_datas = hip_datas
        self.hip = hip
        self.image = image
        self.metrics = metrics
        self.video_clip = video_clip
        self.visual_3d = visual_3d


def retuve_run(
    hip_mode: HipMode,
    config: Config,
    modes_func: GeneralModeFuncType,
    modes_func_kwargs_dict: Dict[str, Any],
    file: str,
) -> RetuveResult:
    """
    Run the Retuve pipeline with standardised inputs and outputs.

    :param hip_mode: The hip mode.
    :param config: The configuration.
    :param modes_func: The mode function.
    :param modes_func_kwargs_dict: The mode function kwargs.
    :param file: The file.

    :return: The Retuve result standardised output.
    """
    always_dcm = (
        len(config.batch.input_types) == 1
        and ".dcm" in config.batch.input_types
    )

    if always_dcm or (
        file.endswith(".dcm") and ".dcm" in config.batch.input_types
    ):
        file = pydicom.dcmread(file)

    if hip_mode == HipMode.XRAY:
        file = Image.open(file)
        hip, image, dev_metrics = analyse_hip_xray_2D(
            file, config, modes_func, modes_func_kwargs_dict
        )
        return RetuveResult(
            hip.json_dump(config, dev_metrics), image=image, hip=hip
        )
    elif hip_mode == HipMode.US3D:
        hip_datas, video_clip, visual_3d, dev_metrics = analyse_hip_3DUS(
            file, config, modes_func, modes_func_kwargs_dict
        )
        return RetuveResult(
            hip_datas.json_dump(config),
            hip_datas=hip_datas,
            video_clip=video_clip,
            visual_3d=visual_3d,
        )
    elif hip_mode == HipMode.US2D:
        file = Image.open(file)
        hip, image, dev_metrics = analyse_hip_2DUS(
            file, config, modes_func, modes_func_kwargs_dict
        )
        return RetuveResult(
            hip.json_dump(config, dev_metrics), hip=hip, image=image
        )
    elif hip_mode == HipMode.US2DSW:
        hip, image, dev_metrics, video_clip = analyse_hip_2DUS_sweep(
            file, config, modes_func, modes_func_kwargs_dict
        )
        return RetuveResult(
            hip.json_dump(config, dev_metrics),
            hip=hip,
            image=image,
            video_clip=video_clip,
        )
    else:
        raise ValueError(f"Invalid hip_mode. {hip_mode}")
