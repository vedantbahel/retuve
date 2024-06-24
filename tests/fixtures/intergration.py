import pydicom
import pytest
from PIL import Image
from radstract.data.dicom import convert_dicom_to_images

XRAY_FILE_PATH = "./tests/test-data/224_DDH_115.jpg"
US_FILE_PATH = "./tests/test-data/171551.dcm"
US_NII_FILE_PATH = "./tests/test-data/171551.nii.gz"


class ResultInfo:
    def __init__(self):
        self.FRAME = 4
        self.FLIPPED = True


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


@pytest.fixture
def us_full_result_info():
    result_info = ResultInfo()
    result_info.FRAME -= 1
    return result_info
