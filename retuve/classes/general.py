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
