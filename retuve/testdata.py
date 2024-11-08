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
        f"{URL}/other/xray/224_DDH_115.jpg",
        f"{URL}/labels/xray/224_DDH_115.json",
    ]
