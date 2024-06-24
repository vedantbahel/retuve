"""
General Drawing Functions used in the retuve package.

"""

from typing import Union

from retuve.classes.draw import Overlay
from retuve.classes.seg import SegFrameObjects
from retuve.hip_us.classes.general import HipDataUS
from retuve.hip_xray.classes import HipDataXray
from retuve.keyphrases.config import Config


def draw_landmarks(
    hip: Union[HipDataUS, HipDataXray], overlay: Overlay
) -> Overlay:
    """
    Draw the landmarks on the overlay.

    :param hip: The hip data.
    :param overlay: The overlay to draw on.

    :return: The overlay with the landmarks drawn.
    """
    if hip.landmarks is None:
        return overlay

    for landmark in hip.landmarks:
        if landmark is None:
            continue

        overlay.draw_cross(landmark)

    return overlay


def draw_seg(
    seg_frame_objs: SegFrameObjects, overlay: Overlay, config: Config
) -> Overlay:
    """
    Draw the segmentation on the overlay.

    :param seg_frame_objs: The segmentation frame objects.
    :param overlay: The overlay to draw on.
    :param config: The configuration.

    :return: The overlay with the segmentation drawn.
    """
    for seg_obj in seg_frame_objs:
        if seg_obj.empty:
            continue

        if seg_obj.points is not None and config.visuals.display_segs:
            overlay.draw_segmentation(seg_obj.points)

        if seg_obj.box is not None and config.visuals.display_boxes:
            overlay.draw_box(seg_obj.box)

        if seg_obj.conf is not None and config.visuals.display_boxes:
            label_text = f"{seg_obj.cls.name}: {seg_obj.conf:.2f}"
            overlay.draw_text(label_text, seg_obj.box[0], seg_obj.box[1])

    return overlay
