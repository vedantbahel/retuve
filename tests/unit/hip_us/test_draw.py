import numpy as np

from retuve.classes.draw import Overlay
from retuve.hip_us.draw import draw_fem_head, draw_hips_us, draw_table


def test_draw_fem_head(hip_data_us_0, fem_sph, config_us):
    overlay = Overlay((512, 512, 3), config_us)
    z_gap = 1.0
    result_overlay = draw_fem_head(hip_data_us_0, fem_sph, overlay, z_gap)

    assert isinstance(result_overlay, Overlay)


def test_draw_hips_us(
    hip_datas_us, results_us, config_us, fem_sph, img_shape_us
):
    images, nifti = draw_hips_us(
        hip_datas_us, results_us, img_shape_us, fem_sph, config_us
    )

    assert isinstance(images, list)
    assert isinstance(images[0], np.ndarray)
    assert images[0].shape == img_shape_us


def test_draw_table(hip_datas_us, img_shape_us):
    image = draw_table(img_shape_us, hip_datas_us)

    assert isinstance(image, np.ndarray)
    assert image.shape == (img_shape_us[0], img_shape_us[1], 3)
