"""
All the subconfigs for Retuve
"""

import os
from typing import Any, Dict, List, Literal, Union

from PIL import ImageFont
from pyparsing import C

from retuve.keyphrases.enums import (
    ACASplit,
    Colors,
    CRFem,
    Curvature,
    HipMode,
    MetricUS,
    MidLineMove,
    Outputs,
)
from retuve.typehints import GeneralModeFuncType

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


class HipConfig:
    def __init__(
        self,
        midline_color: Colors,
        aca_split: ACASplit,
        cr_fem_pos: CRFem,
        fem_extention: float,
        midline_move_method: MidLineMove,
        curvature_method: Curvature,
        measurements: List[MetricUS],
        z_gap: float,
        display_frame_no: bool,
        display_side: bool,
        draw_midline: bool,
        display_fem_guess: bool,
        draw_side_metainfo: bool,
        allow_flipping: bool,
    ):
        """
        The Hip Subconfig.

        :param midline_color (Colors): The color of the midline.
        :param aca_split (ACASplit): The ACA split method.
        :param cr_fem_pos (CRFem): The CR Femoral position.
        :param fem_extention (float): The femoral extention length.
        :param midline_move_method (MidLineMove): The midline move method.
        :param curvature_method (Curvature): The curvature method.
        :param measurements (list): The measurements to calculate.
        :param z_gap (float): The z gap.
        :param display_frame_no (bool): Display the frame number.
        :param display_side (bool): Display the side.
        :param draw_midline (bool): Draw the midline.
        :param display_fem_guess (bool): Display the femoral guess.
        :param draw_side_metainfo (bool): Draw the side metainfo.
        :param allow_flipping (bool): Allow flipping.
        """
        self.midline_color = midline_color
        self.aca_split = aca_split
        self.cr_fem_pos = cr_fem_pos
        self.fem_extention = fem_extention
        self.midline_move_method = midline_move_method
        self.curvature_method = curvature_method
        self.measurements = measurements
        self.z_gap = z_gap
        self.display_frame_no = display_frame_no
        self.display_side = display_side
        self.draw_midline = draw_midline
        self.display_fem_guess = display_fem_guess
        self.draw_side_metainfo = draw_side_metainfo
        self.allow_flipping = allow_flipping


class TrakConfig:
    def __init__(
        self,
        datasets: List[str],
    ):
        """
        Initialize TrakConfig.

        :param datasets (list): The datasets to process.
        """
        self.datasets = datasets


class BatchConfig:
    def __init__(
        self,
        mode_func: GeneralModeFuncType,
        mode_func_args: Dict[str, Any],
        hip_mode: HipMode,
        processes: int,
        input_types: List[Literal[".dcm", ".jpg", ".png"]],
        datasets: List[str],
    ):
        """
        Initialize BatchConfig.

        :param mode_func (callable): The mode function to use.
        :param mode_func_args (dict): The arguments to pass to the mode function.
        :param hip_mode (str): The mode of the hip us.
        :param processes (int): The number of processes to use.
        :param input_types (list): The type of input to use.
        :param datasets (list): The datasets to process.

        :attr outputs (list): The outputs to generate.
        """
        self.mode_func = mode_func
        self.mode_func_args = mode_func_args
        self.hip_mode = hip_mode
        self.processes = processes
        self.input_types = input_types
        self.datasets = datasets

        # set properly upon registration
        self.outputs: List[Outputs] = [Outputs.METRICS]

    def register(self):
        if self.hip_mode == HipMode.US3D:
            self.outputs.append(Outputs.VIDEO_CLIP)
            self.outputs.append(Outputs.VISUAL3D)

        elif self.hip_mode == HipMode.US2D:
            self.outputs.append(Outputs.IMAGE)

        elif self.hip_mode == HipMode.US2DSW:
            self.outputs.append(Outputs.IMAGE)
            self.outputs.append(Outputs.VIDEO_CLIP)

        elif self.hip_mode == HipMode.XRAY:
            self.outputs.append(Outputs.IMAGE)


class APIConfig:
    def __init__(
        self,
        savedir: str,
        url: str,
        db_path: str,
        upload_dir: str,
        hippa_logging_file: str,
        api_token: str,
        origins: List[str],
    ):
        """
        Initialize APIConfig.

        :param savedir (str): The save directory of results.
        :param url (str): The url to serve the API.
        :param db_path (str): The db path.
        :param upload_dir (str): The upload directory.
        :param hippa_logging_file (str): The logging file for HIPPA related logs.
        :param api_token (str): The api token.
        :param origins (list): The origins to allow.
        """
        self.savedir = savedir
        self.url = url
        self.db_path = db_path
        self.upload_dir = upload_dir
        self.hippa_logging_file = hippa_logging_file
        self.api_token = api_token
        self.origins = origins


class VisualsConfig:
    def __init__(
        self,
        font_h1: Union[None, ImageFont.ImageFont],
        font_h2: Union[None, ImageFont.ImageFont],
        default_font_size: int,
        seg_color: Colors,
        seg_alpha: Colors,
        hip_color: Colors,
        bounding_box_color: Colors,
        bounding_box_thickness: int,
        text_color: Colors,
        background_text_color: Colors,
        points_color: Colors,
        points_radius: int,
        line_color: Colors,
        line_thickness: int,
        graf_color: Colors,
        display_full_metric_names: bool,
        display_boxes: bool,
        display_segs: bool,
        scale_image: bool,
    ):
        """
        The Visuals Subconfig.

        :param font_h1 (ImageFont): The font for the h1.
        :param font_h2 (ImageFont): The font for the h2.
        :param default_font_size (int): The default font size.
        :param seg_color (Colors): The color of segmentations.
        :param seg_alpha (Colors): The alpha of segmentations.
        :param hip_color (Colors): The color of hips.
        :param bounding_box_color (Colors): The color of bounding boxes.
        :param bounding_box_thickness (int): The thickness of bounding boxes.
        :param text_color (Colors): The color of text.
        :param background_text_color (Colors): The background color of text.
        :param points_color (Colors): The color of points.
        :param points_radius (int): The radius of points.
        :param line_color (Colors): The color of lines.
        :param line_thickness (int): The thickness of lines.
        :param graf_color (Colors): The color of grafs.
        :param display_full_metric_names (bool): Display full metric names.
        :param display_boxes (bool): Display boxes.
        :param display_segs (bool): Display segmentations.
        :param scale_image (bool): Scale the image.
        """
        self.seg_color = seg_color
        self.seg_alpha = seg_alpha
        self.hip_color = hip_color
        self.bounding_box_color = bounding_box_color
        self.bounding_box_thickness = bounding_box_thickness
        self.text_color = text_color
        self.background_text_color = background_text_color
        self.points_color = points_color
        self.points_radius = points_radius
        self.line_color = line_color
        self.line_thickness = line_thickness
        self.graf_color = graf_color
        self.display_full_metric_names = display_full_metric_names
        self.display_boxes = display_boxes
        self.display_segs = display_segs

        self.font_h1 = font_h1
        self.font_h2 = font_h2
        self.default_font_size = default_font_size
        self.scale_image = scale_image

        if not font_h1:
            self.font_h1 = ImageFont.truetype(
                f"{FILE_DIR}/../files/RobotoMono-Regular.ttf",
                self.default_font_size,
            )

        if not font_h2:
            self.font_h2 = ImageFont.truetype(
                f"{FILE_DIR}/../files/RobotoMono-Regular.ttf",
                self.default_font_size,
            )
