"""
High Level Functions for Multiframe Analysis
"""

import time
from typing import List

import numpy as np
import open3d as o3d
from numpy import ndarray as NDArray
from plotly.graph_objects import Figure

from retuve.classes.seg import SegFrameObjects
from retuve.hip_us.classes.enums import HipLabelsUS, Side
from retuve.hip_us.classes.general import HipDatasUS, Metric3D
from retuve.hip_us.metrics.aca import get_aca
from retuve.hip_us.metrics.c_ratio import get_centering_ratio
from retuve.hip_us.multiframe.models import (
    build_3d_visual,
    get_femoral_sphere,
    get_illium_mesh,
)
from retuve.hip_us.typing import CoordinatesArray3D, FemoralHeadSphere
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import MetricUS
from retuve.logs import ulogger
from retuve.utils import rmean


class FemSphere:
    def __init__(self, center: CoordinatesArray3D, radius: float):
        self.center = center
        self.radius = radius


def get_3d_metrics_and_visuals(
    hip_datas: HipDatasUS, results: List[SegFrameObjects], config: Config
) -> tuple[
    HipDatasUS,
    Figure,
    FemSphere,
    o3d.geometry.TriangleMesh,
    NDArray[np.float64],
    FemoralHeadSphere,
    CoordinatesArray3D,
    CoordinatesArray3D,
]:
    """
    Get the 3D metrics and visuals for the hip US module.

    :param hip_datas: The hip data.
    :param results: The segmentation results.
    :param config: The configuration object.

    :return: The hip data, the 3D visual, the femoral sphere,
             the illium mesh, the apex points, the femoral sphere,
             the average normals data of the ACA Vectors, and the
             normals data of the ACA Vectors.
    """
    start = time.time()
    illium_mesh, apex_points = get_illium_mesh(hip_datas, results, config)
    visual_3d = None

    if illium_mesh is None:
        hip_datas.recorded_error.append("No Illium Mesh.")
        hip_datas.recorded_error.critical = True

    femoral_sphere, radius = get_femoral_sphere(hip_datas, config)

    if illium_mesh:
        aca, avg_normals_data, normals_data, aca_error_msg = get_aca(
            illium_mesh,
            apex_points,
            hip_datas.grafs_hip,
            len(hip_datas),
            config,
        )

        hip_datas.recorded_error.append(aca_error_msg)
    else:
        aca = None
        avg_normals_data = None
        normals_data = None

    if femoral_sphere and illium_mesh:
        c_ratio, cr_points = get_centering_ratio(
            illium_mesh, femoral_sphere, hip_datas, config
        )
        hip_datas.cr_points = cr_points

    else:
        c_ratio = 0
        cr_points = []

    if illium_mesh and femoral_sphere:
        visual_3d = build_3d_visual(
            illium_mesh,
            femoral_sphere,
            avg_normals_data,
            normals_data,
            cr_points,
            hip_datas,
            config,
        )

    if aca:
        aca_metric = Metric3D(
            name=MetricUS.ACA,
            graf=aca[Side.GRAF],
            post=aca[Side.POST],
            ant=aca[Side.ANT],
        )
        hip_datas.metrics.append(aca_metric)

    if c_ratio:
        c_ratio = Metric3D(
            name=MetricUS.CENTERING_RATIO,
            full=c_ratio,
        )
        hip_datas.metrics.append(c_ratio)

    for name in config.hip.measurements:
        if not any(metric.name == name for metric in hip_datas.metrics):
            post_values = [
                hip_data.get_metric(name)
                for hip_data in hip_datas
                if hip_data.side == Side.POST
                and hip_data.get_metric(name) != 0
            ] or [0]
            ant_values = [
                hip_data.get_metric(name)
                for hip_data in hip_datas
                if hip_data.side == Side.ANT and hip_data.get_metric(name) != 0
            ] or [0]

            graf_value = 0
            if hip_datas.graf_frame:
                graf_value = hip_datas.grafs_hip.get_metric(name)

            hip_datas.metrics.append(
                Metric3D(
                    name=name,
                    graf=graf_value,
                    post=rmean(post_values),
                    ant=rmean(ant_values),
                )
            )

    if all(metric.post == 0 for metric in hip_datas.metrics):
        hip_datas.recorded_error.append("No Posterior values recorded.")
        hip_datas.recorded_error.critical = True

    if all(metric.ant == 0 for metric in hip_datas.metrics):
        hip_datas.recorded_error.append("No Anterior values recorded.")
        hip_datas.recorded_error.critical = True
    if len(cr_points) != 0:
        fem_sph = FemSphere(cr_points[0], radius)
    else:
        fem_sph = None

    ulogger.info(
        f"Time for all 3D Elements: {round(time.time() - start, 2)} s"
    )

    return (
        hip_datas,
        visual_3d,
        fem_sph,
        illium_mesh,
        apex_points,
        femoral_sphere,
        avg_normals_data,
        normals_data,
    )


def get_left_apex_angle(hip) -> bool:
    """
    Check if the left apex line is flat.

    :param hip: HipDataUS object.

    :return: Boolean indicating if the left apex line is flat.
    """
    if hip.landmarks is None:
        return True

    C, A, B = (
        np.array(hip.landmarks.left),
        np.array(hip.landmarks.apex),
        np.array((hip.landmarks.apex[0], hip.landmarks.left[1])),
    )

    a = np.linalg.norm(C - B)
    b = np.linalg.norm(C - A)

    angle = np.arccos((a**2 + b**2 - np.linalg.norm(A - B) ** 2) / (2 * a * b))
    angle = np.degrees(angle)

    return int(angle)


def graf_frame_algo(
    hip_zipped_data,
    max_alpha,
    alpha_weight=1,
    angle_weight=0.7,
    os_ishium_weight=1,
):
    """
    Get the Graf Frame for the hip US module as a weighted mix of the max alpha value and flatness of the angle.

    :param hip_zipped_data: The hip data and results.
    :param max_alpha: The Max Alpha
    :param alpha_weight: The weight given to the alpha value in the final mix.
    :param angle_weight: The weight given to the flatness angle in the final mix.
    :param os_ishium_weight: The weight given to the os ishium in the final mix.

    :return: Weighted score based on alpha and flatness.
    """

    hip_data, seg_frame_objs = hip_zipped_data

    # Gives values between 1 and 7
    alpha_value = round(hip_data.get_metric(MetricUS.ALPHA) / max_alpha * 6, 2)

    # Gives values varying between 0 and 10
    left_apex_angle = 10 - get_left_apex_angle(hip_data)

    detected = [seg_obj.cls for seg_obj in seg_frame_objs]
    # Gives a value of 0 or 2
    os_ishium_detected = 3 if HipLabelsUS.OsIchium in detected else 0

    # Calculate the weighted score based on alpha and angle flatness
    final_score = (
        alpha_weight * alpha_value
        + angle_weight * left_apex_angle
        + os_ishium_weight * os_ishium_detected
    )

    return final_score


def find_graf_plane(
    hip_datas: HipDatasUS, results: List[SegFrameObjects]
) -> HipDatasUS:
    """
    Find the Graf Plane for the hip US module.

    :param hip_datas: The hip data.

    :return: The hip data with the Graf Plane.
    """
    any_good_graf_data = [
        (hip_data, seg_frame_objs)
        for hip_data, seg_frame_objs in zip(hip_datas, results)
        if hip_data.metrics
        and all(metric.value != 0 for metric in hip_data.metrics)
    ]

    if len(any_good_graf_data) == 0:
        ulogger.warning("No good graf frames found")
        hip_datas.recorded_error.append("No Perfect Grafs Frames found.")
        hip_datas.recorded_error.critical = True
        any_good_graf_frames = hip_datas.hip_datas
        any_good_graf_data = zip(any_good_graf_frames, results)
    else:
        any_good_graf_frames, _ = zip(*any_good_graf_data)

    # get max alpha frame
    max_alpha = max(
        any_good_graf_frames,
        key=lambda hip_data: hip_data.get_metric(MetricUS.ALPHA),
    ).get_metric(MetricUS.ALPHA)

    if max_alpha == 0:
        hip_datas.recorded_error.append("Max Alpha is 0.")
        hip_datas.recorded_error.critical = True
        return hip_datas

    graf_hip, _ = max(
        any_good_graf_data,
        key=lambda hip_zipped_data: graf_frame_algo(
            hip_zipped_data, max_alpha
        ),
    )

    # pick the index closest to the center
    center = len(hip_datas.hip_datas) // 2
    graf_frame = min(
        [graf_hip.frame_no],
        key=lambda index: abs(index - center),
    )

    hip_datas.graf_frame = graf_frame

    hip_datas.grafs_hip = [
        hip for hip in hip_datas if hip.frame_no == graf_frame
    ][0]

    return hip_datas
