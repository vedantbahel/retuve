import pydicom

from retuve.defaults.hip_configs import default_US
from retuve.defaults.manual_seg import manual_predict_us_dcm
from retuve.funcs import analyse_hip_3DUS
from retuve.testdata import Cases, download_case

# Example usage
dcm_file, seg_file = download_case(Cases.ULTRASOUND_DICOM)

dcm = pydicom.dcmread(dcm_file)

hip_datas, video_clip, visual_3d, dev_metrics = analyse_hip_3DUS(
    dcm,
    keyphrase=default_US,
    modes_func=manual_predict_us_dcm,
    modes_func_kwargs_dict={"seg": seg_file},
)

video_clip.write_videofile("3dus.mp4")
visual_3d.write_html("3dus.html")

metrics = hip_datas.json_dump(default_US)
print(metrics)
