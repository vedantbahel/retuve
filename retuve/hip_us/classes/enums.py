"""
Enums relating to Hip Ultrasound.

"""

from enum import Enum
from typing import List


class Side(Enum):
    """
    For defining how far through a 3D Ultrasound volume the image is taken.
    """

    ANT = 0
    POST = 1
    GRAF = 2

    @classmethod
    def ALL(cls) -> List["Side"]:
        """
        Return all the sides
        """
        return [Side.POST, Side.ANT, Side.GRAF]

    @classmethod
    def get_name(cls, side: "Side") -> str:
        """
        Return the full name of the side from the abbreviation.
        """
        if side == Side.ANT:
            return "Anterior"
        elif side == Side.POST:
            return "Posterior"
        elif side == Side.GRAF:
            return "Central"
        else:
            return "Unknown"


class HipLabelsUS(Enum):
    """
    Segmentation labels for Hip Ultrasound.
    """

    IlliumAndAcetabulum = 0
    FemoralHead = 1
    OsIchium = 2

    @classmethod
    def get_name(cls, label: "HipLabelsUS") -> str:
        """
        Return the full name of the label from the abbreviation.
        """

        if label == HipLabelsUS.IlliumAndAcetabulum:
            return "Illium and Acetabulum"
        elif label == HipLabelsUS.FemoralHead:
            return "Femoral Head"
        elif label == HipLabelsUS.OsIchium:
            return "Os Ichium"
        else:
            return "Unknown"
