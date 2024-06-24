"""
Handles Segmentaitions that are not valid for analysis.
"""

from typing import Dict, List

from PIL import Image

from retuve.classes.seg import SegObject
from retuve.hip_us.classes.enums import HipLabelsUS


def remove_bad_objs(
    hip_objs: Dict[HipLabelsUS, List[SegObject]], img: Image.Image
) -> Dict[HipLabelsUS, SegObject]:
    """
    Remove bad segmentation objects from the Hip Objects.

    For example, if there are multiple segmentations for the Illium and Acetabulum,
    only keep the one that is the most left of the image.

    :param hip_objs: Dict of Hip Objects.
    :param img: Image object.

    """
    if len(hip_objs[HipLabelsUS.IlliumAndAcetabulum]) > 1:
        hip_objs[HipLabelsUS.IlliumAndAcetabulum] = [
            sorted(
                hip_objs[HipLabelsUS.IlliumAndAcetabulum],
                key=lambda seg_obj: seg_obj.box[0],
            )[0]
        ]

    # replace each value with the first element of the list
    for k, v in hip_objs.items():
        if len(v) != 0:
            hip_objs[k] = v[0]
        else:
            hip_objs[k] = SegObject(empty=True)

    illium = hip_objs.get(HipLabelsUS.IlliumAndAcetabulum, None)
    if illium and illium.box is not None and illium.box[0] > img.shape[1] / 2:
        hip_objs[HipLabelsUS.IlliumAndAcetabulum] = SegObject(empty=True)

    return hip_objs
