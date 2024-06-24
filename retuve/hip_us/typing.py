"""
Typehints specific to the hip_us package.
"""

from typing import Tuple

import numpy as np
from numpy.typing import NDArray

FemoralHeadSphere = Tuple[np.ndarray, np.ndarray, np.ndarray]
CoordinatesArray3D = NDArray[np.float64]
