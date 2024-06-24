"""
All unique drawing functions for Hip Ultrasound
"""

import io
import time
from typing import List

import cv2
import numpy as np
import plotly.graph_objects as go
from PIL import Image
from radstract.data.nifti import NIFTI, convert_images_to_nifti_labels

from retuve.classes.draw import Overlay
from retuve.classes.seg import SegFrameObjects
from retuve.draw import draw_landmarks, draw_seg
from retuve.hip_us.classes.enums import Side
from retuve.hip_us.classes.general import HipDatasUS, HipDataUS
from retuve.hip_us.handlers.side import get_side_metainfo
from retuve.hip_us.metrics.alpha import draw_alpha
from retuve.hip_us.metrics.coverage import draw_coverage
from retuve.hip_us.metrics.curvature import draw_curvature
from retuve.hip_us.multiframe import FemSphere
from retuve.hip_us.multiframe.models import circle_radius_at_z
from retuve.keyphrases.config import Config
from retuve.logs import log_timings


def draw_fem_head(
    hip: HipDataUS, fem_sph: FemSphere, overlay: Overlay, z_gap: float
) -> Overlay:
    """
    Draw the femoral head on the image

    :param hip: The Hip Datas
    :param fem_sph: The Femoral Sphere
    :param overlay: The Overlay to draw on

    :return: The Drawn Overlay
    """
    # Get radius at z
    radius = circle_radius_at_z(
        fem_sph.radius, fem_sph.center[2], z_gap * hip.frame_no
    )

    # draw the circle
    overlay.draw_circle((fem_sph.center[0], fem_sph.center[1]), radius)

    return overlay


def draw_hips_us(
    hip_datas: HipDatasUS,
    results: List[SegFrameObjects],
    shape: tuple,
    fem_sph: FemSphere,
    config: Config,
) -> tuple[List[np.ndarray], NIFTI]:
    """
    Draw the hip ultrasound images

    :param hip_datas: The Hip Datas
    :param results: The Segmentation Results
    :param shape: The Shape of the Image
    :param fem_sph: The Femoral Sphere
    :param config: The Config

    :return: The Drawn Images
    """
    draw_timings = []
    image_arrays = []
    nifti_frames = []
    nifti = None

    for hip, seg_frame_objs in zip(hip_datas, results):
        start = time.time()

        overlay = Overlay((shape[0], shape[1], 3), config)

        overlay = draw_seg(seg_frame_objs, overlay, config)

        overlay = draw_landmarks(hip, overlay)

        overlay = draw_alpha(hip, overlay, config)
        overlay = draw_coverage(hip, overlay, config)
        overlay = draw_curvature(hip, overlay, config)

        if fem_sph and config.hip.display_fem_guess:
            overlay = draw_fem_head(
                hip,
                fem_sph,
                overlay,
                config.hip.z_gap,
            )

        overlay = draw_other(
            hip, seg_frame_objs, hip_datas.graf_frame, overlay, config
        )

        img = overlay.apply_to_image(seg_frame_objs.img)

        if config.seg_export:
            test = overlay.get_nifti_frame(seg_frame_objs)
            nifti_frames.append(test)

        image_arrays.append(img)
        draw_timings.append(time.time() - start)

    start = time.time()
    if config.seg_export:
        frames = nifti_frames

        if "Swapped Post and Ant" in hip_datas.recorded_error.errors:
            frames = nifti_frames[::-1]

        # convert to nifti
        nifti = convert_images_to_nifti_labels(frames)
    else:
        nifti = None
    log_timings([time.time() - start], title="Nifti Conversion Speed:")

    log_timings(draw_timings, title="Drawing Speed:")

    return image_arrays, nifti


def draw_other(
    hip: HipDataUS,
    seg_frame_objs: SegFrameObjects,
    graf_frame: int,
    overlay: Overlay,
    config: Config,
) -> Overlay:
    """
    Draw the other meta information on the image

    :param hip: The Hip Data
    :param seg_frame_objs: The Segmentation Frame Objects
    :param graf_frame: The Graf Frame
    :param overlay: The Overlay
    :param config: The Config

    :return: The Drawn Overlay
    """

    if config.hip.display_frame_no:
        # Draw Frame No
        overlay.draw_text(
            f"Frame: {hip.frame_no}",
            0,
            0,
            header="h1",
        )

    shape = seg_frame_objs.img.shape

    # Check if graf alpha
    if hip.frame_no == graf_frame and hip.landmarks:
        overlay.draw_text(
            f"Grafs Frame",
            int(hip.landmarks.left[0]),
            int(hip.landmarks.left[1] - 80),
            header="h2",
            grafs=True,
        )

        # add a border
        overlay.draw_box(
            (0, 0, shape[1], shape[0]),
            grafs=True,
        )

    if hip.landmarks and hip.landmarks.right and config.hip.display_side:
        xl, yl = hip.landmarks.right
        overlay.draw_text(
            f"side: {Side.get_name(hip.side)}",
            int(xl),
            int(yl),
            header="h2",
        )

    if config.hip.draw_midline:
        for seg_obj in seg_frame_objs:
            if seg_obj.midline is not None:
                overlay.draw_skeleton(seg_obj.midline)

            if seg_obj.midline_moved is not None:
                overlay.draw_skeleton(seg_obj.midline_moved)

    if config.hip.draw_side_metainfo:
        closest_illium, mid = get_side_metainfo(hip, seg_frame_objs)
        # these are points, draw them
        if closest_illium is not None:
            overlay.draw_cross(closest_illium)
            overlay.draw_cross(mid)

    return overlay


def draw_table(shape: tuple, hip_datas: HipDatasUS) -> np.ndarray:
    """
    Draw the table of the metrics onto an image

    :param shape: The Shape of the Image
    :param hip_datas: The Hip Datas

    :return: The Image with the Table and any errors
    """
    headers = [""] + hip_datas.metrics[0].names()
    values = []

    for metrics in reversed(hip_datas.metrics):
        values.append(metrics.dump())

    # https://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python
    values = list(zip(*values[::-1]))

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=headers, font=dict(size=24), height=50),
                cells=dict(
                    values=values,
                    fill=dict(color=["paleturquoise", "white"]),
                    font=dict(size=24),
                    height=50,  # Adjust header cell height
                ),
            )
        ]
    )

    MARGIN = 60

    fig.update_layout(
        autosize=False,
        width=shape[1],
        height=shape[0],
        margin=dict(l=MARGIN, r=MARGIN, b=MARGIN, t=MARGIN),
    )

    # save to bytes
    img_bytes = fig.to_image(format="png", width=shape[1], height=shape[0])
    # return PIL image

    # draw the text on the data_image
    data_image = np.array(Image.open(io.BytesIO(img_bytes)).convert("RGB"))

    cv2.putText(
        data_image,
        str(hip_datas.recorded_error),
        (10, data_image.shape[1] - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
    )

    return data_image
