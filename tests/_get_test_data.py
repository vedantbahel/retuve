import gzip
import json
import os
import pickle
import shutil

import open3d as o3d
import pydicom
from PIL import Image

from retuve.defaults.hip_configs import default_US, default_xray
from retuve.defaults.manual_seg import (
    manual_predict_us_dcm,
    manual_predict_xray,
)
from retuve.funcs import analyse_hip_3DUS, analyse_hip_xray_2D
from retuve.testdata import Cases, download_case

# remove if exists and create test-data dir
if os.path.exists("./tests/test-data"):
    shutil.rmtree("./tests/test-data")

os.makedirs("./tests/test-data")

# Example usage
dcm_file, seg_file = download_case(
    Cases.ULTRASOUND_DICOM, directory="./tests/test-data"
)

dcm = pydicom.dcmread(dcm_file)

dcm = pydicom.dcmread(dcm_file)
default_US.test_data_passthrough = True

hip_datas, video_clip, visual_3d, dev_metrics = analyse_hip_3DUS(
    dcm,
    keyphrase=default_US,
    modes_func=manual_predict_us_dcm,
    modes_func_kwargs_dict={"seg": seg_file},
)

illium_mesh = hip_datas.illium_mesh
fem_sph = hip_datas.fem_sph
results = hip_datas.results
apex_points = hip_datas.apex_points
femoral_sphere = hip_datas.femoral_sphere
avg_normals_data = hip_datas.avg_normals_data
normals_data = hip_datas.normals_data
pre_edited_hip_datas = hip_datas.pre_edited_hip_datas
pre_edited_results = hip_datas.pre_edited_results
pre_edited_landmarks = hip_datas.pre_edited_landmarks

# make these elements none in hip_datas now that they are passed through
hip_datas.illium_mesh = None
hip_datas.fem_sph = None
hip_datas.results = None
hip_datas.apex_points = None
hip_datas.femoral_sphere = None
hip_datas.avg_normals_data = None
hip_datas.normals_data = None
hip_datas.pre_edited_hip_datas = None
hip_datas.pre_edited_results = None
hip_datas.pre_edited_landmarks = None

# Save the mesh using open3d
o3d.io.write_triangle_mesh(
    "./tests/test-data/illium_mesh.obj", illium_mesh, write_ascii=True
)

# Save the data
with gzip.open("./tests/test-data/hip_datas_us.pkl.gz", "wb") as f:
    pickle.dump(hip_datas, f)

# Save the mesh as a
with gzip.open("./tests/test-data/fem_sph.pkl.gz", "wb") as f:
    pickle.dump(fem_sph, f)

with gzip.open("./tests/test-data/results_us.pkl.gz", "wb") as f:
    pickle.dump(results, f)

# store apex_points
with gzip.open("./tests/test-data/apex_points.pkl.gz", "wb") as f:
    pickle.dump(apex_points, f)

with gzip.open("./tests/test-data/femoral_sphere.pkl.gz", "wb") as f:
    pickle.dump(femoral_sphere, f)

with gzip.open("./tests/test-data/avg_normals_data.pkl.gz", "wb") as f:
    pickle.dump(avg_normals_data, f)

with gzip.open("./tests/test-data/normals_data.pkl.gz", "wb") as f:
    pickle.dump(normals_data, f)


with gzip.open("./tests/test-data/pre_edited_hip_datas.pkl.gz", "wb") as f:
    pickle.dump(pre_edited_hip_datas, f)

with gzip.open("./tests/test-data/pre_edited_results.pkl.gz", "wb") as f:
    pickle.dump(pre_edited_results, f)

with gzip.open("./tests/test-data/pre_edited_landmarks.pkl.gz", "wb") as f:
    pickle.dump(pre_edited_landmarks, f)

# Create visuals to ensure it works
video_clip.write_videofile("./tests/test-data/video_us.mp4")

visual_3d.write_html("./tests/test-data/visual_3d_us.html")


# Example usage
img_file, labels_json = download_case(
    Cases.XRAY_JPG, directory="./tests/test-data"
)

img_raw = Image.open(img_file)
labels = json.load(open(labels_json))
default_xray.test_data_passthrough = True

hip_data, img, dev_metrics = analyse_hip_xray_2D(
    img_raw,
    keyphrase=default_xray,
    modes_func=manual_predict_xray,
    modes_func_kwargs_dict=labels[0],
)

img.save("./tests/test-data/img_xray.jpg")

seg_results = hip_data.seg_results

hip_data.seg_results = None

# Save the data
with gzip.open("./tests/test-data/hip_data_xray.pkl.gz", "wb") as f:
    pickle.dump(hip_data, f)

with gzip.open("./tests/test-data/seg_results_xray.pkl.gz", "wb") as f:
    pickle.dump(seg_results, f)
