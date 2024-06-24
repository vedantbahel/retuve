"""
Class for creating visual overlays on images.
"""

from enum import Enum
from typing import List, Literal, Tuple

import numpy as np
from PIL import Image, ImageDraw
from radstract.data.colors import LabelColours

from retuve.classes.seg import SegFrameObjects
from retuve.keyphrases.config import Config


class DrawTypes(Enum):
    """
    Enum for the different types of overlays that can be drawn.

    """

    LINES = "lines"
    SEGS = "segs"
    TEXT = "text"
    POINTS = "points"

    @classmethod
    def ALL(cls) -> List["DrawTypes"]:
        return [cls.LINES, cls.SEGS, cls.TEXT, cls.POINTS]


class Overlay:
    """
    Class for creating visual overlays on images.
    """

    def __init__(self, shape: Tuple[int, int], config: Config):
        """
        :param shape: Shape of the image to overlay on.
        :param config: Config object.

        :attr shape: Shape of the image to overlay on.
        :attr overlays: Dictionary of overlays.
        :attr config: Config object.
        """
        self.shape = (shape[0], shape[1], 4)
        self.overlays = {}
        self.config = config

        for drtype in DrawTypes.ALL():
            self.overlays[drtype] = []

    def apply_to_image(self, image: Image.Image) -> np.ndarray:
        """
        Apply stored overlays to an image.

        :param image: Image to apply overlays to.

        :return: Image with overlays applied.
        """
        anno_overlay, seg_overlay = self.get_overlay()

        # convert image to PIL image
        image = Image.fromarray(image).convert("RGBA")

        # change the seg overlay to be semi-transparent
        image = Image.alpha_composite(image, seg_overlay)

        # then paste the annotation overlay
        image = Image.alpha_composite(image, anno_overlay)

        # convert back to numpy array
        # image = image.convert("RGB")
        image = np.array(image, dtype=np.uint8)

        # Remove alpha channel
        image = image[:, :, :3]

        return image

    def get_nifti_frame(self, seg_frame_objs: SegFrameObjects) -> Image.Image:
        """
        Create an image with segmentation overlay ready for NIFTI storage.

        :param seg_frame_objs: Segmentation frame objects.

        :return: Image with segmentation overlay.
        """

        _, seg_overlay = self.blank()

        for seg_obj in seg_frame_objs:
            if not seg_obj.empty:
                # use points to draw polygon
                draw, overlay = self.blank()
                draw.polygon(
                    seg_obj.points,
                    fill=LabelColours.get_color_from_index(
                        seg_obj.cls.value + 1
                    ),
                )

                # convert overlay to rgba
                overlay = overlay.convert("RGBA")
                seg_overlay = Image.alpha_composite(seg_overlay, overlay)

        image = seg_overlay.convert("RGB")

        return image

    def get_overlay(self) -> Tuple[Image.Image, Image.Image]:
        """
        Get all stored overlays as a single image.

        Ensures that they are applied in the correct order.

        :return: Tuple of the annotation overlay and segmentation overlay.
        """
        _, anno_overlay = self.blank()
        _, seg_overlay = self.blank()

        for overlay in self.overlays[DrawTypes.SEGS]:
            seg_overlay = Image.alpha_composite(seg_overlay, overlay)

        for overlay in self.overlays[DrawTypes.LINES]:
            anno_overlay = Image.alpha_composite(anno_overlay, overlay)

        for overlay in self.overlays[DrawTypes.POINTS]:
            anno_overlay = Image.alpha_composite(anno_overlay, overlay)

        for overlay in self.overlays[DrawTypes.TEXT]:
            anno_overlay = Image.alpha_composite(anno_overlay, overlay)

        return anno_overlay, seg_overlay

    def blank(self) -> Tuple[ImageDraw.ImageDraw, Image.Image]:
        """
        Get a blank image and ImageDraw object ready for drawing.

        :return: Tuple of ImageDraw object and blank image.
        """
        data = np.zeros(self.shape, dtype=np.uint8)
        image = Image.fromarray(data).convert("RGBA")
        return ImageDraw.Draw(image), image

    def store(self, overlay, drtype: DrawTypes):
        """
        Store an overlay in the correct category.

        :param overlay: Overlay to store.
        :param drtype: Type of overlay.
        """

        self.overlays[drtype].append(overlay)

    def draw_cross(self, point: Tuple[int, int]):
        """
        Draws a cross of a given radius at a specified point on the overlay.

        :param point: Point to draw the cross at.
        """
        x, y = point
        draw, overlay = self.blank()

        radius = self.config.visuals.points_radius
        color = self.config.visuals.points_color.rgba()

        draw.line(
            (x - radius, y, x + radius, y),
            fill=color,
            width=self.config.visuals.line_thickness,
        )
        draw.line(
            (x, y - radius, x, y + radius),
            fill=color,
            width=self.config.visuals.line_thickness,
        )

        self.store(overlay, DrawTypes.POINTS)

    def draw_segmentation(self, points: List[Tuple[int, int]]):
        """
        Draws a polygon on the overlay.

        :param points: List of points to draw the polygon.
        """
        draw, overlay = self.blank()
        draw.polygon(
            points,
            fill=self.config.visuals.seg_color.rgba(
                self.config.visuals.seg_alpha
            ),
        )

        self.store(overlay, DrawTypes.SEGS)

    def draw_box(self, box: Tuple[int, int, int, int], grafs: bool = False):
        """
        Draws a bounding box on the overlay.

        :param box: Bounding box to draw.
        :param grafs: Whether to draw with the graf frame colours or not.

        """
        x1, y1, x2, y2 = box
        start_point = (int(x1), int(y1))
        end_point = (int(x2), int(y2))  # bottom right corner

        if grafs:
            color = self.config.visuals.graf_color.rgba()
            width = 10
        else:
            color = self.config.visuals.bounding_box_color.rgba()
            width = self.config.visuals.bounding_box_thickness

        draw, overlay = self.blank()
        draw.rectangle(
            [start_point, end_point],
            outline=color,
            width=width,
        )

        self.store(overlay, DrawTypes.LINES)

    def draw_skeleton(self, skel: List[Tuple[int, int]]):
        """
        Draws a skeleton on the overlay.

        :param skel: List of points to draw the skeleton.
        """

        draw, overlay = self.blank()
        for point in skel:
            y, x = point
            # draw a small dot
            draw.point(
                (x, y),
                fill=self.config.hip.midline_color.rgba(),
            )

        self.store(overlay, DrawTypes.POINTS)

    def draw_lines(
        self, line_points: List[Tuple[Tuple[int, int], Tuple[int, int]]]
    ):
        """
        Draws lines on the overlay.

        :param line_points: List of tuples of points to draw lines between.

        """
        # Draw a line between the extreme point and the extra point
        draw, overlay = self.blank()

        for point1, point2 in line_points:
            draw.line(
                (tuple(point1), tuple(point2)),
                fill=self.config.visuals.line_color.rgba(),
                width=self.config.visuals.line_thickness,
            )
        self.store(overlay, DrawTypes.LINES)

    def draw_text(
        self,
        label_text: str,
        x1: int,
        y1: int,
        header: Literal["h1", "h2"] = "h1",
        grafs: bool = False,
    ):
        """
        Draws text on the overlay.

        :param label_text: Text to draw.
        :param x1: x coordinate to draw text.
        :param y1: y coordinate to draw text.
        :param header: Header type to use.
        :param grafs: Whether to draw with the graf frame colours or not.

        """

        draw, overlay = self.blank()

        if header == "h1":
            font = self.config.visuals.font_h1
        elif header == "h2":
            font = self.config.visuals.font_h2

        bbox = draw.textbbox((x1, y1), label_text, font=font)
        if grafs:
            color = self.config.visuals.graf_color.rgba()
        else:
            color = self.config.visuals.background_text_color.rgba()
        draw.rectangle(bbox, fill=color)
        draw.text(
            (x1, y1),
            label_text,
            font=font,
            fill=self.config.visuals.text_color.rgba(),
        )

        self.store(overlay, DrawTypes.TEXT)

    def draw_circle(self, point: Tuple[int, int], radius: int):
        """
        Draws a circle on the overlay.

        :param point: Center of the circle.
        :param radius: Radius of the circle.
        """

        x, y = point
        draw, overlay = self.blank()
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            outline=self.config.visuals.points_color.rgba(),
            width=self.config.visuals.line_thickness,
        )

        self.store(overlay, DrawTypes.POINTS)
