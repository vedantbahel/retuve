# Retuve for Clinicians

Retuve is made up of two main analysis modes:

- DDH Ultrasound: the Standard Alpha Angle and Coverage, as well as other more complicated 3D measurements.
- DDH X-Ray: Currently just acetabular index.

## DDH Ultrasound

Retuve runs 3 seperate DDH Ultrasound Models:

References to more specifics on these indicies can be found here: https://boneandjoint.org.uk/Article/10.1302/2633-1462.311.BJO-2022-0081.R1/pdf

### 3D Ultrasound

**Please Note that the 2D Sweep and 3D DICOMs are sythetically stitched together from 2D Graf Hips, so do not expect accurate results. We are working on getting a 3DUS Case on a Creative Commons License to have as an example.**

Retuve makes the following measurements in a 3D Hip Ultrasound:
- Alpha Angle
- Coverage
- Curvature (A measure of the shape of the acetabulum/illium bone)
- ACA (Acetabular Coverage Angle) (A more precise 3D Alpha Angle)
- Centering Ratio (A measure of the femoral head position in 3D space)

We calculate the 2D measurements in 3D by finding the average in the:
- Graf Plane (including +/- 5% in average)
- Posterior
- Anterior

Alpha, Coverage and Curvature are visible on videos created by retuve, which can be seen here: (If you are on Github: see https://github.com/radoss-org/radoss-creative-commons/raw/main/other/ultrasound/172535.mp4)

Attribution of the above Ultrasound Images: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172535 (https://radiopaedia.org/cases/172535)


<video width="500" controls>
  <source src="https://github.com/radoss-org/radoss-creative-commons/raw/main/other/ultrasound/172535.mp4" type="video/mp4">
</video>

Attribution of the above Ultrasound Images: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172535 (https://radiopaedia.org/cases/172535)

The Centering Ratio and ACA values are not as easy to visualise, but can be seen in the following 3D Figure: (If you are on Github: see https://html-preview.github.io/?url=https://github.com/radoss-org/radoss-creative-commons/raw/main/other/ultrasound/172535.html)

<iframe src="https://html-preview.github.io/?url=https://github.com/radoss-org/radoss-creative-commons/raw/main/other/ultrasound/172535.html" width="700" height="500"></iframe>

Derivative from Radiopedia: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172535 (https://radiopaedia.org/cases/172535)

### 2D Ultrasound

Retuve makes the following measurements in a 2D Hip Ultrasound:
- Alpha Angle
- Coverage
- Curvature (A measure of the shape of the acetabulum/illium bone)

They can all be seen on the below image.

<img src="https://raw.githubusercontent.com/radoss-org/radoss-creative-commons/main/other/ultrasound/172535_0_processed.png" alt="drawing" width="500"/>

Attribution of the above Ultrasound Images: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172535 (https://radiopaedia.org/cases/172535)

### 2D Sweep Ultrasound (Experimental/Limited Testing)

**Please Note that the 2D Sweep and 3D DICOMs are sythetically stitched together from 2D Graf Hips, so do not expect accurate results. We are working on getting a 3DUS Case on a Creative Commons License to have as an example.**

2D Sweep Ultrasound is essentially 2D Ultrasound, with the added ability to detect which frame of a video/dicom to select
for analysis. This is useful for scans that have not been processed already.

## DDH X-Ray

Retuve runs a single DDH X-Ray Model, which measures the Acetabular Index.

This is visualised by an image created when Retuve Runs.

<img src="https://github.com/radoss-org/radoss-creative-commons/blob/main/other/xray/331_DDH_115_processed.jpg?raw=true" alt="drawing" width="500"/>

Attribution of the above X-Ray Images: Fraiwan, Mohammad; Al-Kofahi, Noran; Hanatleh, Omar; ibnian, ali (2022), “A dataset of DDH x-ray images”, Mendeley Data, V2, doi: 10.17632/jf3pv98m9g.2