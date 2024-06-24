from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import ImageDraw

from retuve.classes.draw import DrawTypes, Overlay


@pytest.fixture
def overlay(config_xray):
    return Overlay((100, 100), config_xray)


def test_initialization(overlay):
    assert overlay.shape == (100, 100, 4)
    assert len(overlay.overlays) == len(DrawTypes.ALL())
    for drtype in DrawTypes.ALL():
        assert overlay.overlays[drtype] == []


def test_blank_method(overlay):
    draw, image = overlay.blank()
    assert isinstance(draw, ImageDraw.ImageDraw)
    assert image.size == (100, 100)
    assert image.mode == "RGBA"


def test_store_method(overlay):
    draw, image = overlay.blank()
    overlay.store(image, DrawTypes.POINTS)
    assert len(overlay.overlays[DrawTypes.POINTS]) == 1
    assert overlay.overlays[DrawTypes.POINTS][0] == image


def test_draw_cross(overlay):
    overlay.draw_cross((50, 50))
    assert len(overlay.overlays[DrawTypes.POINTS]) == 1


def test_draw_segmentation(overlay):
    points = [(10, 10), (20, 10), (20, 20), (10, 20)]
    overlay.draw_segmentation(points)
    assert len(overlay.overlays[DrawTypes.SEGS]) == 1


def test_draw_box(overlay):
    box = (10, 10, 20, 20)
    overlay.draw_box(box)
    assert len(overlay.overlays[DrawTypes.LINES]) == 1


def test_draw_skeleton(overlay):
    skeleton = [(10, 10), (20, 20)]
    overlay.draw_skeleton(skeleton)
    assert len(overlay.overlays[DrawTypes.POINTS]) == 1


def test_draw_lines(overlay):
    line_points = [((10, 10), (20, 20))]
    overlay.draw_lines(line_points)
    assert len(overlay.overlays[DrawTypes.LINES]) == 1


def test_draw_text(overlay):
    overlay.draw_text("Test", 10, 10, header="h1")
    assert len(overlay.overlays[DrawTypes.TEXT]) == 1


def test_draw_circle(overlay):
    overlay.draw_circle((50, 50), 10)
    assert len(overlay.overlays[DrawTypes.POINTS]) == 1


def test_apply_to_image(overlay):
    # Create a dummy image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    overlay.draw_cross((50, 50))
    result_image = overlay.apply_to_image(image)
    assert result_image.shape == (100, 100, 3)


def test_get_nifti_frame(overlay):
    seg_frame_objs = [
        MagicMock(
            empty=False,
            points=[(10, 10), (20, 10), (20, 20), (10, 20)],
            cls=MagicMock(value=1),
        )
    ]
    image = overlay.get_nifti_frame(seg_frame_objs)
    assert image.size == (100, 100)
    assert image.mode == "RGB"
