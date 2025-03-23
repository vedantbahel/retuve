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
Segmentaition Classes

These are the classes you need to store your model results in.

They are used so Retuve can understand the results of your model.

Below is an example of how to write a custom AI model and config for Retuve.

https://github.com/radoss-org/retuve/tree/main/examples/ai_plugins/custom_ai_and_config.py

```python
.. include:: ../../examples/ai_plugins/custom_ai_and_config.py
```

This file can then be used with the UI and Trak using.

```bash
retuve --task trak --keyphrase_file config.py
```
"""

from typing import Annotated, Iterable, List, Literal, Tuple, TypeVar

import numpy as np
import numpy.typing as npt
from PIL import Image
from radstract.data.colors import get_unique_colours

from retuve.hip_us.classes.enums import HipLabelsUS
from retuve.hip_xray.classes import HipLabelsXray

DType = TypeVar("DType", bound=np.generic)

NDArrayImg_NxNx3 = Annotated[npt.NDArray[DType], Literal["N", "N", 3]]
NDArrayImg_NxNx3_AllWhite = Annotated[npt.NDArray[DType], Literal["N", "N", 3]]
MidLine = List[Tuple[int, int]]


class SegObject:
    """
    Class for holding a single segmentation object.
    """

    def __init__(
        self,
        points: List[Tuple[int, int]] = None,
        clss: HipLabelsUS = None,
        mask: NDArrayImg_NxNx3_AllWhite = None,
        conf: float = None,
        box: Tuple[int, int, int, int] = None,
        empty: bool = False,
    ):
        """
        :param points: List of points that make up the object.
        :param clss: Class of the object.
        :param mask: Mask of the object.
        :param conf: Confidence of the object.
        :param box: Bounding box of the object.
        :param empty: Is the object empty.

        :attr midline: Midline of the object (Only for Hip Ultrasound).
        :attr midline_moved: Midline of the object after it
              has been moved (Only for Hip Ultrasound).

        :raises ValueError: If any of the parameters are not as expected.
        """
        self.points = points
        self.cls = clss
        self.mask = mask
        self.box = box
        self.conf = conf
        self.empty = empty

        # Only for hip_us
        self.midline: MidLine = None
        self.midline_moved: MidLine = None

        if empty:
            return

        if points is not None:
            for point in points:
                if len(point) != 2:
                    raise ValueError("Point is not a tuple of length 2")

        if type(mask) != np.ndarray:
            raise ValueError("mask is not a numpy array")

        # check mask shape
        if len(mask.shape) != 3 or mask.shape[2] != 3:
            raise ValueError("mask is not RGB as required")

        colors = get_unique_colours(array=mask)
        # check each pixel in mask is either rgb white or black
        if (
            any(color not in [(0, 0, 0), (255, 255, 255)] for color in colors)
            or len(colors) > 2
        ):
            raise ValueError("mask is not all white")

        if box is not None:
            if len(box) != 4:
                raise ValueError("box is not a tuple of length 4")

        if clss is None or not (
            isinstance(clss, int)
            or isinstance(clss, HipLabelsUS)
            or isinstance(clss, HipLabelsXray)
        ):
            raise ValueError("clss is None or wrong type")

        if conf is not None and not 0 <= conf <= 1:
            raise ValueError("conf is not None and not between 0 and 1")

    def __str__(self):
        return f"SegObject({self.cls}, {self.conf}, {self.points})"

    def area(self):
        """
        Returns the area of the object.
        """
        # Use the mask to calculate the area
        if self.mask is None:
            return 0
        return np.sum(self.mask[:, :, 0] == 255)

    def flip_horizontally(self, img_width: int):
        """
        Flips the object horizontally.

        :param img_width: Width of the image.
        """
        if self.empty:
            return

        if self.box is not None:
            self.box = (
                img_width - self.box[2],
                img_width - self.box[0],
                self.box[1],
                self.box[3],
            )

        if self.points is not None:
            self.points = [(img_width - x, y) for x, y in self.points]

        if self.midline is not None:
            self.midline = np.array(
                [(y, img_width - x) for y, x in self.midline]
            )

        if self.midline_moved is not None:
            self.midline_moved = np.array(
                [(y, img_width - x) for y, x in self.midline_moved]
            )

        if self.mask is not None:
            self.mask = np.flip(self.mask, axis=1)


class SegFrameObjects:
    """
    Class for holding a frame of segmentation objects.
    """

    def __init__(
        self, img: NDArrayImg_NxNx3, seg_objects: list[SegObject] = None
    ):
        """
        :param img: Image of the frame.
        :param seg_objects: List of segmentation objects in the frame.
        """
        if type(img) != np.ndarray:
            raise ValueError("img is not a numpy array")

        if seg_objects is None:
            seg_objects = []

        self.seg_objects = seg_objects
        self.img = img

    def __iter__(self) -> Iterable[SegObject]:
        return iter(self.seg_objects)

    def append(self, seg_result: SegObject):
        self.seg_objects.append(seg_result)

    def __getitem__(self, index):
        return self.seg_objects[index]

    def __setitem__(self, index, value):
        self.seg_objects[index] = value

    def __len__(self):
        return len(self.seg_objects)

    @classmethod
    def empty(cls, img: Image.Image):
        """
        Returns an empty SegFrameObjects object.

        :param img: Image of the frame.
        """

        return cls(img=img, seg_objects=[SegObject(empty=True)])

    def __str__(self):
        return f"SegFrameObjects({self.seg_objects})"
