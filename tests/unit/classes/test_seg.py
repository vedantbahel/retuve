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

import numpy as np
import pytest

from retuve.classes.seg import SegFrameObjects, SegObject
from retuve.hip_us.classes.enums import HipLabelsUS


def create_dummy_image(shape=(100, 100, 3), color=(255, 255, 255)):
    img = np.ones(shape, dtype=np.uint8) * np.array(color, dtype=np.uint8)
    return img


def test_SegObject_init():
    points = [(0, 0), (1, 1)]
    clss = HipLabelsUS.FemoralHead
    mask = create_dummy_image()
    conf = 0.9
    box = (0, 0, 10, 10)

    seg_obj = SegObject(points, clss, mask, conf, box)
    assert seg_obj.points == points
    assert seg_obj.cls == clss
    assert np.array_equal(seg_obj.mask, mask)
    assert seg_obj.conf == conf
    assert seg_obj.box == box


def test_SegObject_init_empty():
    seg_obj = SegObject(empty=True)
    assert seg_obj.empty


def test_SegObject_init_invalid_point():
    with pytest.raises(ValueError, match="Point is not a tuple of length 2"):
        SegObject(points=[(0, 0, 0)])


def test_SegObject_init_invalid_mask():
    with pytest.raises(ValueError, match="mask is not a numpy array"):
        SegObject(mask="not an array")


def test_SegObject_init_invalid_mask_shape():
    with pytest.raises(ValueError, match="mask is not RGB as required"):
        SegObject(mask=np.zeros((100, 100, 1)))


def test_SegObject_init_invalid_mask_colors():
    invalid_mask = create_dummy_image(color=(255, 0, 0))
    with pytest.raises(ValueError, match="mask is not all white"):
        SegObject(mask=invalid_mask)


def test_SegObject_init_invalid_box():
    with pytest.raises(ValueError, match="box is not a tuple of length 4"):
        SegObject(box=(0, 0, 10), mask=create_dummy_image())


def test_SegObject_init_invalid_class():
    with pytest.raises(ValueError, match="clss is None or wrong type"):
        SegObject(clss="not a valid class", mask=create_dummy_image())


def test_SegObject_init_invalid_conf():
    with pytest.raises(ValueError, match="conf is not None and not between 0 and 1"):
        SegObject(clss=1, conf=1.5, mask=create_dummy_image())


def test_SegFrameObjects_init():
    img = create_dummy_image()
    seg_objs = [SegObject(empty=True)]
    seg_frame_objs = SegFrameObjects(img, seg_objs)
    assert seg_frame_objs.img is img
    assert seg_frame_objs.seg_objects == seg_objs


def test_SegFrameObjects_init_invalid_img():
    with pytest.raises(ValueError, match="img is not a numpy array"):
        SegFrameObjects(img="not an array")


def test_SegFrameObjects_empty():
    img = create_dummy_image()
    seg_frame_objs = SegFrameObjects.empty(img)
    assert seg_frame_objs.img is img
    assert len(seg_frame_objs) == 1
    assert seg_frame_objs[0].empty


def test_SegFrameObjects_append():
    img = create_dummy_image()
    seg_frame_objs = SegFrameObjects(img)
    seg_obj = SegObject(empty=True)
    seg_frame_objs.append(seg_obj)
    assert len(seg_frame_objs) == 1
    assert seg_frame_objs[0] is seg_obj


def test_SegFrameObjects_iter():
    img = create_dummy_image()
    seg_objs = [SegObject(empty=True) for _ in range(3)]
    seg_frame_objs = SegFrameObjects(img, seg_objs)
    for i, seg_obj in enumerate(seg_frame_objs):
        assert seg_obj is seg_objs[i]


def test_SegFrameObjects_len():
    img = create_dummy_image()
    seg_objs = [SegObject(empty=True) for _ in range(3)]
    seg_frame_objs = SegFrameObjects(img, seg_objs)
    assert len(seg_frame_objs) == 3
