import json

from PIL import Image

from retuve.defaults.hip_configs import default_xray
from retuve.defaults.manual_seg import manual_predict_xray
from retuve.funcs import analyse_hip_xray_2D
from retuve.testdata import Cases, download_case

# Example usage
img_file, labels_json = download_case(Cases.XRAY_JPG)

img_raw = Image.open(img_file)
labels = json.load(open(labels_json))

hip_data, img, dev_metrics = analyse_hip_xray_2D(
    img_raw,
    keyphrase=default_xray,
    modes_func=manual_predict_xray,
    modes_func_kwargs_dict=labels[0],
)

img.save("xray.jpg")
img_raw.save("xray-raw.jpg")

metrics = hip_data.json_dump(default_xray, dev_metrics)
print(metrics)
