"""
The Default Segmentaition Method for Hip Ultrasound and Xray.

Currently, all the defaults are manual methods.

AI methods will be added in the future.
"""

import time
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
import pydicom
from nibabel.nifti1 import Nifti1Image
from PIL import Image, ImageOps
from radstract.data.colors import LabelColours, get_unique_colours
from radstract.data.dicom import convert_dicom_to_images
from radstract.data.nifti import convert_nifti_to_image_labels

from retuve.classes.seg import SegFrameObjects, SegObject
from retuve.hip_us.classes.enums import HipLabelsUS
from retuve.hip_xray.classes import HipLabelsXray, LandmarksXRay
from retuve.keyphrases.config import Config
from retuve.logs import log_timings


def manual_predict_us_dcm(
    dcm: pydicom.FileDataset,
    keyphrase: Union[str, Config],
    config: Config = None,
    seg: Union[str, Nifti1Image] = None,
) -> List[SegFrameObjects]:
    """
    Manual Segmentation for Hip Ultrasound.

    :param dcm: The DICOM File
    :param keyphrase: The Keyphrase or Config
    :param config: The Config
    :param seg: The Segmentation File

    :return: The Segmentation Results
    """
    if not config:
        config = Config.get_config(keyphrase)

    dicom_images = convert_dicom_to_images(
        dcm,
        crop_coordinates=config.crop_coordinates,
        dicom_type=config.dicom_type,
    )

    return manual_predict_us(dicom_images, keyphrase, config=config, seg=seg)


def manual_predict_us(
    images: List[Image.Image],
    keyphrase: Union[str, Config],
    config: Config = None,
    seg: Union[str, Nifti1Image] = None,
    seg_idx: int = 0,
) -> List[SegFrameObjects]:
    """
    Manual Segmentation for Hip Ultrasound.

    :param images: The Images
    :param keyphrase: The Keyphrase or Config
    :param config: The Config
    :param seg: The Segmentation File
    :param seg_idx: The Segmentation Index

    :return: The Segmentation Results
    """

    if not config:
        config = Config.get_config(keyphrase)

    # seg is a nifti file, open it
    if not seg:
        raise ValueError("seg file is required")

    results, _ = convert_nifti_to_image_labels(
        seg, crop_coordinates=config.crop_coordinates
    )

    if seg_idx:
        results = results[seg_idx:]

    classes = {
        LabelColours.LABEL1: HipLabelsUS.IlliumAndAcetabulum,
        LabelColours.LABEL2: HipLabelsUS.FemoralHead,
        LabelColours.LABEL3: HipLabelsUS.OsIchium,
    }

    timings = []
    seg_results = []

    for img, result in zip(images, results):
        start = time.time()
        img = np.array(img)

        seg_frame_objects = SegFrameObjects(img)

        # get each colour from the seg
        unique_colours = get_unique_colours(result)

        # convert image to np array
        for colour in unique_colours:
            if colour not in classes:
                continue

            # convert image to np array
            result = np.array(result)

            mask = np.all(result == colour, axis=-1)
            mask = mask.astype(np.uint8) * 255

            # get the bounding box
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                continue

            box = cv2.boundingRect(mask)
            # just get the bottom left and top right coordinates
            box = (box[0], box[1], box[0] + box[2], box[1] + box[3])

            # get the points on the outside of the mask
            points = np.concatenate(contours[0], axis=0)

            # drop 80% of the points
            points = [
                (int(x), int(y))
                for i, (x, y) in enumerate(points)
                if i % 10 == 0
            ]

            # convert mask to rgb
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

            seg_obj = SegObject(
                points, classes[colour], mask, box=box, conf=1.0
            )

            seg_frame_objects.append(seg_obj)

        timings.append(time.time() - start)

        if len(seg_frame_objects) == 0:
            seg_frame_objects = SegFrameObjects.empty(img=img)

        seg_results.append(seg_frame_objects)

    log_timings(timings, title="Manual Segmentation")

    return seg_results


def manual_predict_xray(
    images: List[Image.Image],
    keyphrase: Union[str, Nifti1Image],
    config: Config = None,
    landmark_list: List[Dict[str, List[int]]] = None,
    scale_landmarks: bool = False,
) -> Tuple[List[LandmarksXRay], List[SegFrameObjects]]:
    """
    Manual Segmentation for Hip Xray.

    :param images: The Images
    :param keyphrase: The Keyphrase or Config
    :param config: The Config
    :param landmark_list: The Landmark List
    :param scale_landmarks: Whether to scale the landmarks.
                            This shoudl be set False if your coordinates
                            are calculated to the 1024x1024 image resize.

    :return: The Landmarks and Segmentation Results
    """
    if not config:
        config = Config.get_config(keyphrase)

    original_wh = [images[0].width, images[0].height]

    if not landmark_list:
        raise ValueError("landmark_list is required")

    landmark_results = []
    seg_results = []

    for image, landmarks in zip(images, landmark_list):
        A, B = image.size

        if scale_landmarks:
            for key, (x, y) in landmarks.items():
                landmarks[key] = (
                    int(x * A / original_wh[0]),
                    int(y * B / original_wh[1]),
                )

        landmarks = LandmarksXRay(**landmarks)
        landmarks_l = [landmarks.pel_l_o, landmarks.pel_l_i, landmarks.fem_l]
        landmarks_r = [landmarks.pel_r_o, landmarks.pel_r_i, landmarks.fem_r]

        # construct masks for the triangles
        mask_l = np.zeros((A, B, 3), dtype=np.uint8)
        mask_r = np.zeros((A, B, 3), dtype=np.uint8)

        cv2.fillPoly(mask_l, [np.array(landmarks_l)], (255, 255, 255))
        cv2.fillPoly(mask_r, [np.array(landmarks_r)], (255, 255, 255))

        # and bounding boxes
        box_l = cv2.boundingRect(np.array(landmarks_l))
        box_r = cv2.boundingRect(np.array(landmarks_r))

        # get the bottom left and top right coordinates
        box_l = (box_l[0], box_l[1], box_l[0] + box_l[2], box_l[1] + box_l[3])
        box_r = (box_r[0], box_r[1], box_r[0] + box_r[2], box_r[1] + box_r[3])

        image = np.array(image)

        seg_objects = [
            SegObject(
                landmarks_l,
                HipLabelsXray.AceTriangle,
                mask_l,
                box=box_l,
                conf=1.0,
            ),
            SegObject(
                landmarks_r,
                HipLabelsXray.AceTriangle,
                mask_r,
                box=box_r,
                conf=1.0,
            ),
        ]
        seg_result = SegFrameObjects(img=image, seg_objects=seg_objects)

        seg_results.append(seg_result)
        landmark_results.append(landmarks)

    return landmark_results, seg_results
