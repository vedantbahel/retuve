"""
Drawing code related to hip xray images.
"""

import time
from typing import List

from numpy.typing import NDArray
from PIL import Image

from retuve.classes.draw import Overlay
from retuve.classes.seg import SegFrameObjects
from retuve.draw import draw_landmarks, draw_seg
from retuve.hip_xray.classes import HipDataXray
from retuve.hip_xray.metrics.ace import draw_ace
from retuve.keyphrases.config import Config
from retuve.logs import log_timings


def draw_hips_xray(
    hip_datas: List[HipDataXray],
    results: List[SegFrameObjects],
    shape: tuple,
    config: Config,
) -> List[NDArray]:
    """
    Draw the hip xray images

    :param hip_datas: The Hip Datas
    :param results: The Segmentation Results
    :param shape: The Shape of the Image
    :param config: The Config

    :return: The Drawn Images as Numpy Arrays
    """
    draw_timings = []
    image_arrays = []

    for hip, seg_frame_objs in zip(hip_datas, results):
        start = time.time()

        overlay = Overlay((shape[0], shape[1], 3), config)

        overlay = draw_seg(seg_frame_objs, overlay, config)

        overlay = draw_landmarks(hip, overlay)

        overlay = draw_ace(hip, overlay, config)

        img = overlay.apply_to_image(seg_frame_objs.img)

        image_arrays.append(img)
        draw_timings.append(time.time() - start)

    log_timings(draw_timings, title="Drawing Speed:")

    return image_arrays
