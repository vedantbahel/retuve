"""
Default Working Configs for Retuve

Import them directly from the retuve package.

We don't store them, so that the Retuve UI does not use them.
"""

from retuve.keyphrases.enums import OperationType

from .config import base_config

default_US = base_config.get_copy()
default_US.visuals.default_font_size = 40
default_US.visuals.points_radius = 15
default_US.visuals.line_thickness = 4
default_US.visuals.bounding_box_thickness = 10
default_US.hip.display_side = False

default_US.register(name="default_US", store=False)

default_xray = base_config.get_copy()
default_xray.operation_type = OperationType.LANDMARK
default_xray.visuals.points_radius = 10
default_xray.visuals.line_thickness = 3
default_xray.visuals.default_font_size = 30
default_xray.visuals.bounding_box_thickness = 7

default_xray.register(name="default_xray", store=False)
