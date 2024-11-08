import gzip
import json
import os
import pickle
import shutil
from datetime import datetime
from difflib import unified_diff
from hmac import new

import open3d as o3d
import pydicom
import yaml
from PIL import Image
from radstract.data.dicom import convert_dicom_to_images

from retuve.defaults.hip_configs import default_US, default_xray
from retuve.defaults.manual_seg import (
    manual_predict_us,
    manual_predict_us_dcm,
    manual_predict_xray,
)
from retuve.funcs import (
    analyse_hip_2DUS,
    analyse_hip_2DUS_sweep,
    analyse_hip_3DUS,
    analyse_hip_xray_2D,
)
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

test_data_dir = "./tests/test-data"

# Save the mesh using open3d
o3d.io.write_triangle_mesh(
    f"{test_data_dir}/illium_mesh.obj", illium_mesh, write_ascii=True
)

# Save json
json_file_3dus = hip_datas.json_dump(default_US)

# Save the data
with gzip.open(f"{test_data_dir}/hip_datas_us.pkl.gz", "wb") as f:
    pickle.dump(hip_datas, f)

# Save the mesh as a
with gzip.open(f"{test_data_dir}/fem_sph.pkl.gz", "wb") as f:
    pickle.dump(fem_sph, f)

with gzip.open(f"{test_data_dir}/results_us.pkl.gz", "wb") as f:
    pickle.dump(results, f)

# store apex_points
with gzip.open(f"{test_data_dir}/apex_points.pkl.gz", "wb") as f:
    pickle.dump(apex_points, f)

with gzip.open(f"{test_data_dir}/femoral_sphere.pkl.gz", "wb") as f:
    pickle.dump(femoral_sphere, f)

with gzip.open(f"{test_data_dir}/avg_normals_data.pkl.gz", "wb") as f:
    pickle.dump(avg_normals_data, f)

with gzip.open(f"{test_data_dir}/normals_data.pkl.gz", "wb") as f:
    pickle.dump(normals_data, f)


with gzip.open(f"{test_data_dir}/pre_edited_hip_datas.pkl.gz", "wb") as f:
    pickle.dump(pre_edited_hip_datas, f)

with gzip.open(f"{test_data_dir}/pre_edited_results.pkl.gz", "wb") as f:
    pickle.dump(pre_edited_results, f)

with gzip.open(f"{test_data_dir}/pre_edited_landmarks.pkl.gz", "wb") as f:
    pickle.dump(pre_edited_landmarks, f)

# Create visuals to ensure it works
video_clip.write_videofile(f"{test_data_dir}/video_us.mp4")

visual_3d.write_html(f"{test_data_dir}/visual_3d_us.html")


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

# Save json
json_file_xray = hip_data.json_dump(default_xray, dev_metrics)

img.save(f"{test_data_dir}/img_xray.jpg")

seg_results = hip_data.seg_results

hip_data.seg_results = None

# Save the data
with gzip.open(f"{test_data_dir}/hip_data_xray.pkl.gz", "wb") as f:
    pickle.dump(hip_data, f)

with gzip.open(f"{test_data_dir}/seg_results_xray.pkl.gz", "wb") as f:
    pickle.dump(seg_results, f)


# Get jsons for 2DSW and 2D

hip_datas, _, dev_metrics, _ = analyse_hip_2DUS_sweep(
    dcm=dcm,
    keyphrase=default_US,
    modes_func=manual_predict_us_dcm,
    modes_func_kwargs_dict={"seg": seg_file},
)

json_file_us_sweep = hip_datas.json_dump(default_US, dev_metrics)

images = convert_dicom_to_images(dcm)

hip_data, _, dev_metrics = analyse_hip_2DUS(
    img=images[0],
    keyphrase=default_US,
    modes_func=manual_predict_us,
    modes_func_kwargs_dict={"seg": seg_file},
)

json_file_us = hip_data.json_dump(default_US, dev_metrics)


# ==============================================================================


def load_previous_release_note():
    # Locate the most recent YAML file in ./changenotes/
    release_dir = "./changenotes/"
    yaml_files = [f for f in os.listdir(release_dir) if f.endswith(".yaml")]
    # sort by date (most recent first)
    yaml_files.sort(reverse=True)
    if yaml_files:
        with open(os.path.join(release_dir, yaml_files[0]), "r") as f:
            return yaml.safe_load(f), yaml_files[0]
    return None, None


def has_changes(new_data, old_data):
    # Change recorded error to None in both if "" or None
    if new_data["3dus"]["recorded_error"] in ["", None]:
        new_data["3dus"]["recorded_error"] = None
    if old_data["3dus"]["recorded_error"] in ["", None]:
        old_data["3dus"]["recorded_error"] = None

    # Compare for changes as JSON's
    changes = json.dumps(new_data, sort_keys=True) != json.dumps(
        old_data, sort_keys=True
    )

    # Print diff
    if changes:
        diff = unified_diff(
            json.dumps(old_data, indent=4).splitlines(),
            json.dumps(new_data, indent=4).splitlines(),
            lineterm="",
        )
        print("\n".join(diff))
    return changes


# Helper function to add comments for modified YAML values
def mark_changes(new_data, old_data, path=""):
    if isinstance(new_data, dict):
        # Recursively compare dictionaries
        for key in new_data.keys():
            full_path = f"{path}.{key}" if path else key
            if key in old_data:
                new_data[key] = mark_changes(
                    new_data[key], old_data[key], full_path
                )
            else:
                # Key is new, mark it as added
                new_data[key] = f"{new_data[key]}  # Added"
    elif isinstance(new_data, list):
        # Compare lists by index
        for i in range(len(new_data)):
            if i < len(old_data):
                new_data[i] = mark_changes(
                    new_data[i], old_data[i], f"{path}[{i}]"
                )
            else:
                # Item is new in the list
                new_data[i] = f"{new_data[i]}  # Added"
    else:
        # Direct value comparison for basic data types
        if new_data != old_data:
            # Mark value as modified
            new_data = f"{new_data}  # Modified"
    return new_data


# Load previous release note
previous_data, previous_filename = load_previous_release_note()

# Merge the json files, save as YAML
merged_json = {
    "description": "Your description here.",
    "current_output": {
        "3dus": json_file_3dus,
        "xray": json_file_xray,
        "us_sweep": json_file_us_sweep,
        "2dus": json_file_us,
    },
}

json_str = json.dumps(merged_json, default=str)
standardized_data = json.loads(json_str)

# Check for changes
if previous_data is None or has_changes(
    standardized_data["current_output"], previous_data["current_output"]
):
    if previous_data:
        new_current_output = mark_changes(
            standardized_data["current_output"],
            previous_data["current_output"],
        )
        annotated_data = {
            "description": standardized_data["description"],
            "current_output": new_current_output,
        }
    else:
        annotated_data = standardized_data

    # Prepare filename and save as YAML
    today = datetime.today().strftime("%Y-%m-%d")
    new_filename = f"./changenotes/{today}_title-here.yaml"

    with open(new_filename, "w") as f:
        yaml.dump(annotated_data, f, sort_keys=False)

    # Modify values with # Modified, by removing all quotes
    with open(new_filename, "r") as f:
        content = f.read()
        content = content.replace("'", "")
        content = content.replace(
            "recorded_error:   # Modified", "recorded_error: ''"
        )
    with open(new_filename, "w") as f:
        f.write(content)

    print(f"New release note saved as {new_filename}")

    print(
        "\nWARNING\n"
        "=======================\n"
        "You have made changes to the output of Retuve. "
        "Please ensure these changes are intended \nand either minor, "
        "or making meaningful clinical improvements."
    )
else:
    print("No changes detected; no new release note created.")
