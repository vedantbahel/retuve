"""
Provides a convenient way to download test data for the Retuve library.
"""

import os
from enum import Enum

import requests

URL = (
    "https://raw.githubusercontent.com/radoss-org/radoss-creative-commons/main"
)


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


def download_case(case: Cases, directory: str = None, temp=True) -> list:
    """
    Download the test data for the given case

    :param case: The Case
    :param directory: The directory to download the files to
    :param temp: Whether to download the files to a temporary directory
    :return: The filenames of the downloaded files

    Note that when directory is provided, temp is ignored.
    """
    if directory:
        temp = False

    if temp:
        # the directory should be in /tmp
        directory = "/tmp/retuve-testdata"

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    filenames = []

    for index, url in enumerate(case.value):

        url_filename = url.split("/")[-1]
        # Extract the filename from the URL
        filename = os.path.join(directory, url_filename)

        # Download the file
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Downloaded {filename}")
        else:
            print(
                f"Failed to download {url}, status code: {response.status_code}"
            )

        filenames.append(filename)

    return filenames
