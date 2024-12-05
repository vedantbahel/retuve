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

import json

import pydicom
import pytest
from PIL import Image
from radstract.data.dicom import convert_dicom_to_images

XRAY_FILE_PATH = "./tests/test-data/331_DDH_115.jpg"
US_FILE_PATH = "./tests/test-data/171551.dcm"
US_NII_FILE_PATH = "./tests/test-data/171551.nii.gz"


@pytest.fixture
def xray_file_path():
    return XRAY_FILE_PATH


@pytest.fixture
def us_file_path():
    return US_FILE_PATH


@pytest.fixture
def us_nii_file_path():
    return US_NII_FILE_PATH


@pytest.fixture
def xray_image():
    return Image.open(XRAY_FILE_PATH)


@pytest.fixture
def us_images():
    dcm = pydicom.dcmread(US_FILE_PATH)
    return convert_dicom_to_images(dcm)


@pytest.fixture
def us_dcm():
    return pydicom.dcmread(US_FILE_PATH)
