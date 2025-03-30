# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Metric: Acetabular Coverage Angle (ACA)

Meant to be a more accurate version of alpha angle for 3D Ultrasounds.

"""

import copy
from enum import Enum
from typing import Dict, List, Tuple

import numpy as np
import open3d as o3d
from numpy.typing import NDArray

from retuve.hip_us.classes.enums import Side
from retuve.hip_us.classes.general import HipDataUS
from retuve.hip_us.typing import CoordinatesArray3D
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import ACASplit
from retuve.utils import warning_decorator


class SideZ(Enum):
    """
    Enuum for side of the Illiac-Acetabular Bone view for each 2D Frame
    """

    LEFT = "illiac wing"
    RIGHT = "acetabular roof"


"""
Matches the colors of the ACA to the side and third of the Illium.
"""
ACA_COLORS = {
    (SideZ.LEFT, Side.POST): "red",
    (SideZ.LEFT, Side.GRAF): "orange",
    (SideZ.LEFT, Side.ANT): "yellow",
    (SideZ.RIGHT, Side.POST): "blue",
    (SideZ.RIGHT, Side.GRAF): "cyan",
    (SideZ.RIGHT, Side.ANT): "lightgreen",
}


class Triangle:
    """
    Class to store the data of a triangle for the ACA calculation.

    :attr apex_side: SideZ: The side of the Illium that the apex is on.
    :attr third: Side: The third of the Illium that the triangle is in.
    :attr normal: NDArray[np.float64]: The normal of the triangle.
    :attr centroid: NDArray[np.float64]: The centroid of the triangle.
    :attr color: str: The color of the triangle.
    """

    def __init__(
        self,
        apex_side: SideZ,
        third: Side,
        normal: NDArray[np.float64],
        centroid: NDArray[np.float64],
    ):
        self.apex_side = apex_side
        self.third = third
        self.normal = normal
        self.centroid = centroid
        self.color = ACA_COLORS[(apex_side, third)]


@warning_decorator(alpha=True)
def get_aca(
    illium_mesh: o3d.geometry.TriangleMesh,
    apex_points: NDArray[np.float64],
    graf_hip: HipDataUS,
    no_of_frames: int,
    config: Config,
) -> Tuple[
    Dict[Side, float],
    Tuple[CoordinatesArray3D, CoordinatesArray3D, str],
    List[Triangle],
    str,
]:
    """
    Calculate the acetabular coverage angle (ACA) for the hip.

    :param illium_mesh (o3d.geometry.TriangleMesh): The Illium Mesh.
    :param apex_points (NDArray[np.float64]): The apex points of the Illium.
    :param graf_hip (HipDataUS): The Hip Data of the Graf Frame.
    :param no_of_frames (int): The number of frames in the 3D Ultrasound.
    :param config (Config): The Config object.

    :return: Tuple of the ACA angles for each side, the average normals data,
             the triangle data, and the recorded error.
    """
    z_gap = config.hip.z_gap * (200 / no_of_frames)

    # add normals as arrows
    illium_mesh.compute_vertex_normals()
    normals = np.asarray(illium_mesh.vertex_normals)
    vertices = np.asarray(illium_mesh.vertices)

    # Compute triangle normals
    triangle_normals = []
    triangle_centroids = []
    for tri in illium_mesh.triangles:
        v0, v1, v2 = vertices[tri]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        centroid = (v0 + v1 + v2) / 3
        triangle_normals.append(normal)
        triangle_centroids.append(centroid)

    triangle_normals = np.array(triangle_normals)
    triangle_centroids = np.array(triangle_centroids)

    # convert normals to unit vectors
    triangle_normals /= np.linalg.norm(triangle_normals, axis=1)[:, None]

    triangle_data = []

    max_z = np.max(triangle_centroids[:, 2])
    min_z = np.min(triangle_centroids[:, 2])

    for normal, centroid in zip(triangle_normals, triangle_centroids):
        if config.hip.aca_split == ACASplit.THIRDS:
            third_z = (max_z - min_z) / 3

            # find which third the centroid is in
            if centroid[2] - min_z < third_z:
                third = Side.POST
            elif centroid[2] - min_z < third_z * 2:
                third = Side.GRAF
            else:
                third = Side.ANT

        elif config.hip.aca_split == ACASplit.GRAFS:
            grafs_z = graf_hip.frame_no * z_gap

            grafs_z = grafs_z

            margin = (max_z - min_z) * 0.15

            min_graf_z = grafs_z - margin

            # if it is within 10% of the grafs_z, third = 2
            if abs(centroid[2] - grafs_z) < margin:
                third = Side.GRAF
            elif centroid[2] < min_graf_z:
                third = Side.POST
            else:
                third = Side.ANT

        else:
            raise ValueError("Invalid ACA Split Config Option")

        apex_points = copy.deepcopy(np.array(apex_points))

        # get the apex point with the closest z value
        apex_point = apex_points[np.argmin(np.abs(apex_points[:, 2] - centroid[2]))]

        if centroid[0] < apex_point[0]:
            apex_side = SideZ.LEFT
        else:
            apex_side = SideZ.RIGHT

        triangle_data.append(
            Triangle(
                apex_side,
                third,
                normal,
                centroid,
            )
        )

    final_vectors = {
        # (left, 1): vec
    }

    avg_normals_data = []

    # for each color combination, find the average normal and add a cone for it
    for apex_side in [SideZ.LEFT, SideZ.RIGHT]:
        for third in Side.ALL():
            normals = []
            centroids = []

            for triangle in triangle_data:
                if triangle.apex_side == apex_side and triangle.third == third:
                    normals.append(triangle.normal)
                    centroids.append(triangle.centroid)

            # This error is recorded in other places.
            # And will happen when the grafs plane is detected
            # At the edges of the measured region
            if len(normals) == 0:
                continue

            normals = np.array(normals)
            centroids = np.array(centroids)

            avg_normal = np.mean(normals, axis=0)
            avg_centroid = np.mean(centroids, axis=0)

            avg_normals_data.append(
                (
                    avg_normal,
                    avg_centroid,
                    ACA_COLORS[(apex_side, third)],
                )
            )

            final_vectors[apex_side, third] = avg_normal

    aca_angles = {}

    # for each third, find the angle between the apex left and right
    for side in Side.ALL():
        try:
            apex_left = final_vectors[SideZ.LEFT, side]
            apex_right = final_vectors[SideZ.RIGHT, side]
            recorded_error = ""
        except KeyError:
            aca_angles[side] = 0
            recorded_error = f"Not enough {Side.get_name(side)} to calculate ACA."
            continue

        # get the angle between the two apex points
        angle = np.arccos(
            np.dot(apex_left, apex_right)
            / (np.linalg.norm(apex_left) * np.linalg.norm(apex_right))
        )

        # convert to degrees
        angle = np.degrees(angle)

        aca_angles[side] = round(angle, 2)

    return aca_angles, avg_normals_data, triangle_data, recorded_error
