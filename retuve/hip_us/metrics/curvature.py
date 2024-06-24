"""
Metric: Curvature

An experimental metric that calculates the "curvature" of the hip.

Overtime, there will be different versions of this metric as it is
still being developed. Which version will be controlled from the config.
"""

import math
from typing import Tuple

import numpy as np

from retuve.classes.draw import Overlay
from retuve.hip_us.classes.general import HipDataUS, LandmarksUS
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import Curvature, MetricUS


def find_curvature(
    landmarks: LandmarksUS, shape: Tuple, config: Config
) -> float:
    """
    Calculate the curvature of the hip.

    :param landmarks: LandmarksUS: The landmarks object.
    :param shape: Tuple: The shape of the image.
    :param config: Config: The Config object.

    :return: float: The curvature of the hip.
    """
    if not (
        landmarks and landmarks.left and landmarks.apex and landmarks.right
    ):
        return 0

    if config.hip.curvature_method == Curvature.RADIST:
        width = shape[1]

        # This normalisation factor can handle bad crmodes,
        # As well as off-center scans
        normalise_factor = abs((width // 2) - landmarks.left[0])

        total_distance = 0

        for a, b in [
            (landmarks.left, landmarks.apex),
            (landmarks.right, landmarks.apex),
        ]:
            # Get the distance between two points in 2D space
            distance_x = abs(a[0] - b[0])
            distance_y = abs(a[1] - b[1])

            # Calculate the distance between the two points
            distance = math.sqrt(distance_x**2 + distance_y**2)

            # Normalise the distance
            distance /= normalise_factor

            # Add the distance to the total distance
            total_distance += distance

        # Calculate the angle of landmarks.left, landmarks.apex, landmarks.right
        # This is the angle of the triangle
        A, B, C = (
            np.array(landmarks.left),
            np.array(landmarks.apex),
            np.array(landmarks.right),
        )
        AB = np.linalg.norm(A - B)
        BC = np.linalg.norm(B - C)
        AC = np.linalg.norm(A - C)
        # in radians
        angle = np.arccos((BC**2 + AB**2 - AC**2) / (2 * BC * AB))

        curvature = round(angle / total_distance, 2)

    else:
        raise ValueError(f"Curvature method {config.hip.curvature} not found")

    return curvature


def draw_curvature(
    hip: HipDataUS, overlay: Overlay, config: Config
) -> Overlay:
    """
    Draw the curvature of the hip.

    :param hip: HipDataUS: The HipDataUS object.
    :param overlay: Overlay: The Overlay object.
    :param config: Config: The Config object.

    :return: Overlay: The Overlay object.
    """
    curvature = hip.get_metric(MetricUS.CURVATURE)

    if config.visuals.display_full_metric_names:
        title = "Curvature"
    else:
        title = "Cur"

    if curvature != 0:
        overlay.draw_text(
            f"{title}: {curvature}",
            int(hip.landmarks.left[0]),
            int(hip.landmarks.left[1] - 240),
            header="h2",
        )

    return overlay
