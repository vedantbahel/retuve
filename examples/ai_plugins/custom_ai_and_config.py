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

from typing import List

import my_model
import pydicom

from retuve.classes.seg import SegFrameObjects, SegObject
from retuve.defaults.hip_configs import default_US
from retuve.funcs import analyse_hip_3DUS
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import HipMode
from retuve.testdata import Cases, download_case


# NOTE: Can accept any number of arguments.
def custom_ai_model(dcm, keyphrase, kwarg1, kwarg2) -> List[SegFrameObjects]:
    # Ensures keyphrase is converted to config if its not already
    config = Config.get_config(keyphrase)

    results = my_model.predict(dcm, ...)
    seg_results = []

    # Each result represents results for a single frame.
    for result in results:

        seg_frame_objects = SegFrameObjects(img=result.img)

        # there can be multiple objects in a single frame,
        # even of the same class.
        for box, class_, points, conf, mask in result:

            seg_obj = SegObject(points, class_, mask, box=box, conf=conf)
            seg_frame_objects.append(seg_obj)

        seg_results.append(seg_frame_objects)

    return seg_results


# NOTE: Needs to be called "setup" to be picked up by the Retuve API.
def setup():
    chop = default_US.get_copy()
    chop.device = 0
    chop.batch.mode_func = custom_ai_model
    chop.batch.mode_func_args = {
        "kwarg1": "value1",
        "kwarg2": "value2",
    }
    chop.batch.hip_mode = HipMode.US3D

    chop.register(name="chop")

    return chop


# Example usage
dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

dcm = pydicom.dcmread(dcm_file)

CHOP = setup()

dcm = pydicom.dcmread(dcm_file)

hip_datas, video_clip, visual_3d, dev_metrics = analyse_hip_3DUS(
    dcm,
    keyphrase=CHOP,  # can also be "chop"
    modes_func=custom_ai_model,
    modes_func_kwargs_dict={"seg": seg_file},
)

video_clip.write_videofile("3dus.mp4")
visual_3d.write_html("3dus.html")

metrics = hip_datas.json_dump(default_US)
print(metrics)
