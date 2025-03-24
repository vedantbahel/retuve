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

import copy

import numpy as np
import pytest

from retuve.classes.seg import SegObject
from retuve.hip_us.classes.enums import HipLabelsUS
from retuve.hip_us.handlers.segs import remove_bad_objs


@pytest.fixture
def single_illium_objs(results_us):
    all_illium_objs = []
    for result in results_us:
        illium_objs = [
            seg_obj
            for seg_obj in result
            if seg_obj.cls == HipLabelsUS.IlliumAndAcetabulum
        ]

        all_illium_objs.extend(illium_objs)

    illium_obj = all_illium_objs[0]

    hip_objs = {
        HipLabelsUS.IlliumAndAcetabulum: [illium_obj],
        HipLabelsUS.FemoralHead: [],
        HipLabelsUS.OsIchium: [],
    }

    return hip_objs, results_us[0].img


@pytest.fixture
def multiple_illium_objs(results_us):
    all_illium_objs = []
    for result in results_us:
        illium_objs = [
            seg_obj
            for seg_obj in result
            if seg_obj.cls == HipLabelsUS.IlliumAndAcetabulum
        ]

        all_illium_objs.extend(illium_objs)

    illium_obj = all_illium_objs[0]

    illium_obj2 = copy.deepcopy(illium_obj)
    illium_obj2.box = [
        illium_obj.box[0],
        illium_obj.box[1] + 100,
        illium_obj.box[2],
        illium_obj.box[3] + 100,
    ]

    # roll the mask with numpy
    illium_obj2.mask = np.roll(illium_obj2.mask, 100, axis=1)

    hip_objs = {
        HipLabelsUS.IlliumAndAcetabulum: [illium_obj, illium_obj2],
        HipLabelsUS.FemoralHead: [],
        HipLabelsUS.OsIchium: [],
    }

    return hip_objs, results_us[0].img


def test_remove_bad_objs(single_illium_objs):
    hip_objs_before, img = single_illium_objs
    hip_objs = copy.deepcopy(hip_objs_before)

    hip_objs, *_ = remove_bad_objs(hip_objs, img)
    assert isinstance(hip_objs[HipLabelsUS.IlliumAndAcetabulum], SegObject)
    assert (
        hip_objs[HipLabelsUS.IlliumAndAcetabulum].box
        == hip_objs_before[HipLabelsUS.IlliumAndAcetabulum][0].box
    )


def test_remove_bad_objs_multiple(multiple_illium_objs):
    hip_objs_before, img = multiple_illium_objs
    hip_objs = copy.deepcopy(hip_objs_before)

    hip_objs, *_ = remove_bad_objs(hip_objs, img)
    assert isinstance(hip_objs[HipLabelsUS.IlliumAndAcetabulum], SegObject)

    # check the right object was removed
    assert (
        hip_objs[HipLabelsUS.IlliumAndAcetabulum].box
        == hip_objs_before[HipLabelsUS.IlliumAndAcetabulum][0].box
    )
