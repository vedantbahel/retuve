![Retuve](https://files.mcaq.me/52kj1.png)

# Retuve - The first Open, Collaborative Framework for Infant Hip Health using AI

Retuve (from the scottish gaelic `Ri taobh` meaning `beside`) is a framework for analysing infant hips. It is designed to be a flexible and extensible framework that can be used by developers, AI researchers and clinicians.

It takes in raw Hip Ultrasound and X-Ray images, and outputs a report with the labelled images, and the results, exactly as a clinician would.

<img src="https://raw.githubusercontent.com/radoss-org/radoss-creative-commons/main/other/224_ddh_115_%26_172535_0_diagram.jpg" alt="drawing" width="500"/>

Attribution of the above Ultrasound Images: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172535 (https://radiopaedia.org/cases/172535)

Attribution of the above X-Ray Images: Fraiwan, Mohammad; Al-Kofahi, Noran; Hanatleh, Omar; ibnian, ali (2022), “A dataset of DDH x-ray images”, Mendeley Data, V2, doi: 10.17632/jf3pv98m9g.2

# License

Retuve is licensed under the Apache 2.0 License. This means that you can use it for commercial purposes, and modify it as you see fit. The only requirement is that you must provide the license with any distribution of the software.

# Quickstart

**Please Note that the 2D Sweep and 3D DICOMs are sythetically stitched together from 2D Graf Hips, so do not expect accurate results. We are working on getting a 3DUS Case on a Creative Commons License to have as an example.**

To get started with Retuve, you can install it via pip:

```bash
pip install git+https://github.com/radoss-org/retuve.git
```

You can then run the following code to get a basic report:

```python
import pydicom
from radstract.data.dicom import convert_dicom_to_images
from retuve.defaults.hip_configs import default_US
from retuve.defaults.manual_seg import manual_predict_us
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

img.save("2dus.png")
```
<img src="https://raw.githubusercontent.com/radoss-org/radoss-creative-commons/main/other/ultrasound/172535_0_processed.png" alt="drawing" width="500"/>

Attribution of the above Ultrasound Images: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172535 (https://radiopaedia.org/cases/172535)

# Features

- pip installable (easy to intergrate with you existing systems)
- Apache 2.0 Licensed
- AI is fully pluggable/modular
- Basic Web Interface bundled (through Retuve Trak)
- CLI Interface
- Swagger API Provided (through Retuve Trak)

# Examples

Examples can be found at https://github.com/radoss-org/retuve/tree/main/examples

# Docs

We provide high level overviews for different types of users. This includes a tailored description of Retuve, and some highlighted features:

- [For Developers](docs/overviews/for_developers.md)
- [For AI Researchers](docs/overviews/for_ai_researchers.md)
- [For Clinicians](docs/overviews/for_clinicians.md)

# Modalities

Retuve can analyse Hips for:

- [Ultrasound](docs/modalities/ultrasound.md)
- [X-Ray](docs/modalities/xray.md)


# Developer Guide

You can clone the repository and install the dependencies with the following command:

```bash
git clone https://github.com/radoss-org/retuve.git
```

You can then install retuve with poetry, and then run the tests:

**NOTE: These tests are about testing consistency between changes, and not directly testing the accuracy of the AI. See `changenotes` for tracking.**

```bash
# Needed for the scripts
pip install poethepoet

cd retuve
poetry install

# Generate the test data
poe testgen

# Run all tests, including examples.
poe test_all

# Get info on all other dev scripts
poe help
```

# Immediate Roadmap

- [ ] Add Default Apache 2.0 Licensed AI Plugins
- [ ] Add Documentaition for Retuve Trak
- [ ] Create Apache 2.0 Licensed Dataset and Benchmark

# Invitation for Collaboration

We are looking for support on the following:

- [ ] Landmark Models

We also accept any new algorithms for the different metrics, with the option to switch back to the old method provided through the config.
