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
Other general classes that are used in the project.
"""


class RecordedError:
    """
    Class for storing errors as they occur during processing.

    Can be critical or non-critical, and frame-dependent or not.
    """

    def __init__(self):
        self.errors = []
        self.frame_dependent_errors = {}
        self.critical = False

    def __str__(self) -> str:
        str_errors = self.errors.copy()

        for frame_no, errors in self.frame_dependent_errors.items():
            str_errors.append(f"Frame {frame_no}: {', '.join(errors)}")

        return " ".join(str_errors)

    def append(self, error: str, frame_no: int = None):
        """
        Append an error to the list of errors.

        :param error: Error to append.
        :param frame_no: Frame number the error occurred on. (If required)
        """

        if not frame_no:
            self.errors.append(error)

        else:
            if frame_no not in self.frame_dependent_errors:
                self.frame_dependent_errors[frame_no] = []
            self.frame_dependent_errors[frame_no].append(error)

    def __bool__(self):
        return len(self.errors) > 0
