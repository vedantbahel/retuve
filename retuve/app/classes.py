# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


class LiveResponse(BaseModel):
    file_id: str
    video_url: str
    img_url: str


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
