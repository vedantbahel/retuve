import pydicom

from retuve.defaults.hip_configs import default_US
from retuve.defaults.manual_seg import manual_predict_us_dcm
from retuve.funcs import analyse_hip_2DUS_sweep
from retuve.testdata import Cases, download_case

# Example usage
dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

dcm = pydicom.dcmread(dcm_file)

hip_datas, img, dev_metrics, video_clip = analyse_hip_2DUS_sweep(
    dcm,
    keyphrase=default_US,
    modes_func=manual_predict_us_dcm,
    modes_func_kwargs_dict={"seg": seg_file},
)

video_clip.write_videofile("2dus_sweep.mp4")
img.save("2dus_sweep.png")

metrics = hip_datas.json_dump(default_US, dev_metrics)
print(metrics)
