"""
All the input/output structure classes used to power the Retuve API.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from retuve.hip_us.classes.general import Metric2D, Metric3D


class FileEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    IMCOMPLETE = "incomplete"
    FAILED = "failed"
    DEAD = "dead"
    DEAD_WITH_RESULTS = "dead_with_results"

    def __str__(self):
        return self.name


class Metric2D(BaseModel):
    """
    Any 2D metric.
    """

    name: str
    value: float


class Metric3D(BaseModel):
    """
    Any 3D metric.
    """

    name: str
    post: float
    graf: float
    ant: float
    full: float


class ModelResponse(BaseModel):
    """
    The output of a Retuve Model.
    """

    notes: str
    metrics_3d: Optional[List[Metric3D]]
    metrics_2d: Optional[List[Metric2D]]
    video_url: Optional[str]
    figure_url: Optional[str]
    img_url: Optional[str]
    retuve_version: str
    keyphrase_name: str


class File(BaseModel):
    """
    The details attached to any file analyzed by Retuve.
    """

    file_id: str
    state: FileEnum
    metrics_url: str
    video_url: str
    img_url: str
    figure_url: str
    attempts: int


class SystemFiles(BaseModel):
    """
    The files in the Retuve System.
    """

    states: List[File]
    length: int


class FeedbackRequest(BaseModel):
    """
    The feedback request for any file.
    """

    file_id: str
    feedback: str
