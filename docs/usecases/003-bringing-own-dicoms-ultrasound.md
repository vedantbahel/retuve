# Bringing Your Own Ultrasound DICOMs

This guide will show you how to analyze your own Ultrasound DICOMs using Retuve. Retuve supports three types of ultrasound analysis:
- 2D Ultrasound (single frame)
- 3D Ultrasound (volume)
- 2D Sweep Ultrasound (multiple frames)

## Install Retuve's AI Plugins

As of 2025-06-01, Retuve does not include default AI plugins. You will need to install an external plugin. The following plugins are available:

**Note:**
All plugins are under their own licenses. Please check the license of each plugin before using it.

- [retuve-tinyunet-plugin](https://github.com/radoss-org/retuve-tinyunet-plugin)
- [retuve-nnunet-plugin](https://github.com/radoss-org/retuve-nnunet-plugin)
- [retuve-yolo-plugin](https://github.com/radoss-org/retuve-yolo-plugin)

For this guide, we will use the `retuve-yolo-plugin`.

Install it with:

```bash
pip install git+https://github.com/radoss-org/retuve-yolo-plugin
```

## Creating a Minimal Script

You only need to make a few changes to the example scripts to run the AI on your own data.

### 1. Import the Ultrasound Plugin and Required Modules

```python
from retuve_yolo_plugin.ultrasound import yolo_predict_dcm_us
import pydicom
from PIL import Image
```

### 2. Load Your Own DICOM File(s)

You can load either a single DICOM file or a list of DICOM files:

```python
# For single DICOM file
dcm_file = "path/to/your/dicom/file.dcm"
dcm = pydicom.dcmread(dcm_file)
```

## Example Scripts

### 2D Ultrasound Analysis

Here is a complete example script for analyzing a single 2D ultrasound frame:

```python
import pydicom
from radstract.data.dicom import DicomTypes
from retuve_yolo_plugin.ultrasound import yolo_predict_dcm_us

from retuve.defaults.hip_configs import default_US
from retuve.funcs import analyse_hip_2DUS

dcm_file = "./your/dicom/file.dcm"
dcm = pydicom.dcmread(dcm_file)
default_US.dicom_type = DicomTypes.SINGLE

hip, img, dev_metrics = analyse_hip_2DUS(
    dcm,
    keyphrase=default_US,
    modes_func=yolo_predict_dcm_us,
    modes_func_kwargs_dict={},
)

img.save("ultrasound_2d.jpg")
metrics = hip.json_dump(default_US, dev_metrics)
```

Note that you can also supply this function a pillow image. See https://github.com/radoss-org/retuve/blob/main/examples/high_level_functions/2dus.py

### 3D Ultrasound Analysis

For 3D ultrasound analysis:

```python
import pydicom
from retuve_yolo_plugin.ultrasound import yolo_predict_dcm_us

from retuve.defaults.hip_configs import default_US
from retuve.funcs import analyse_hip_3DUS

dcm_file = "./your/dicom/file.dcm"
dcm = pydicom.dcmread(dcm_file)

hip_datas, video_clip, visual_3d, dev_metrics = analyse_hip_3DUS(
    dcm,
    keyphrase=default_US,
    modes_func=yolo_predict_dcm_us,
    modes_func_kwargs_dict={},
)

video_clip.write_videofile("ultrasound_3d.mp4")
visual_3d.write_html("ultrasound_3d_visual.html")
metrics = hip_datas.json_dump(default_US)
```

Note that you can also supply this function a list of pillow images. See https://github.com/radoss-org/retuve/blob/main/tests/intergration/test_funcs.py#L144

### 2D Sweep Ultrasound Analysis

For 2D sweep ultrasound analysis:

```python
import pydicom
from retuve_yolo_plugin.ultrasound import yolo_predict_dcm_us

from retuve.defaults.hip_configs import default_US
from retuve.funcs import analyse_hip_2DUS_sweep

dcm_file = "./your/dicom/file.dcm"
dcm = pydicom.dcmread(dcm_file)

hip, img, dev_metrics, video_clip = analyse_hip_2DUS_sweep(
    dcm,
    keyphrase=default_US,
    modes_func=yolo_predict_dcm_us,
    modes_func_kwargs_dict={},
)

img.save("ultrasound_2dsw_graf.jpg")
video_clip.write_videofile("ultrasound_2dsw.mp4")
metrics = hip.json_dump(default_US, dev_metrics)
```

Note that you can also supply this function a pillow image. See https://github.com/radoss-org/retuve/blob/main/tests/intergration/test_funcs.py#L165

## Troubleshooting

## Further Reading

- [Retuve Documentation](https://retuve.nidusai.ca/retuve.html)
- [YOLO Plugin for Retuve](https://github.com/radoss-org/retuve-yolo-plugin)

---

**Note:**
All plugins are under their own licenses. Please check the license of each plugin before using it.

---

If you need to process individual files or want more control, see the [minimal script guide](https://github.com/radoss-org/retuve/tree/main/examples/high_level_functions). example in the other part of this codebase.