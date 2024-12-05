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
Useful Type Hints for the Retuve package.
"""

from typing import (
    Annotated,
    Any,
    BinaryIO,
    Callable,
    Dict,
    List,
    Literal,
    Tuple,
    TypeVar,
    Union,
)

import numpy as np
import numpy.typing as npt
import pydicom
from PIL import Image

from retuve.classes.seg import SegFrameObjects
from retuve.hip_xray.classes import LandmarksXRay

DType = TypeVar("DType", bound=np.generic)

"""The type of retuves expected mask"""
NDArrayImg_NxNx3_AllWhite = Annotated[npt.NDArray[DType], Literal["N", "N", 3]]

"""The expected type of midlines"""
MidLine = List[Tuple[int, int]]

"""Any acceptable file-like object."""
FileLike = Union[BinaryIO, Image.Image, pydicom.FileDataset]

"""Keyphrase as a string or a config"""
KeyphraseLike = Union[str, List[str]]

"""The expected form of AI Model Functions for the retuve package"""
GeneralModeFuncType = Callable[
    [
        FileLike,
        KeyphraseLike,
        Dict[str, Any],
    ],
    Union[
        Tuple[List[LandmarksXRay], List[SegFrameObjects]],
        List[SegFrameObjects],
    ],
]
