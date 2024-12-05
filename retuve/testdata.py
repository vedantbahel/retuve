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
Provides a convenient way to download test data for the Retuve library.
"""

from enum import Enum

from radstract.testdata import download_case

URL = (
    "https://raw.githubusercontent.com/radoss-org/radoss-creative-commons/main"
)

download_case = download_case


class Cases(Enum):
    """
    The test cases available for download.
    """

    ULTRASOUND_DICOM = [
        f"{URL}/dicoms/ultrasound/171551.dcm",
        f"{URL}/labels/ultrasound/171551.nii.gz",
    ]

    XRAY_JPG = [
        f"{URL}/other/xray/331_DDH_115.jpg",
        f"{URL}/labels/xray/331_DDH_115.json",
    ]
