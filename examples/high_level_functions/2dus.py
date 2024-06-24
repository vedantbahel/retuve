import pydicom
from radstract.data.dicom import convert_dicom_to_images

from retuve.defaults.hip_configs import default_US
from retuve.defaults.manual_seg import manual_predict_us
from retuve.funcs import analyse_hip_2DUS
from retuve.testdata import Cases, download_case

# Example usage
dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

dcm = pydicom.dcmread(dcm_file)

images = convert_dicom_to_images(dcm)

hip_data, img, dev_metrics = analyse_hip_2DUS(
    images[0],
    keyphrase=default_US,
    modes_func=manual_predict_us,
    modes_func_kwargs_dict={"seg": seg_file},
)

images[0].save("2dus-raw.png")
img.save("2dus.png")

metrics = hip_data.json_dump(default_US, dev_metrics)
print(metrics)
