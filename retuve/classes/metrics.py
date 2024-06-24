"""
Metric Classes for all Retuve Models.
"""

from typing import List, Union


class Metric2D:
    """
    2D Metrics just have a name and a value.
    """

    def __init__(self, name: str, value: Union[int, float]):
        """
        Initialize a 2D Metric.

        :param name: Name of the metric.
        :param value: Value of the metric.
        """
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"Metric2D(name={self.name}, value={self.value})"


class Metric3D:
    """
    3D Metrics have a name and 4 values: Post, Graf, Ant, Full.
    """

    def __init__(
        self,
        name: str,
        post: Union[float, str] = 0,
        graf: Union[float, str] = 0,
        ant: Union[float, str] = 0,
        full: Union[float, None] = None,
    ):
        """
        If full is not not provided, it is calculated as the average of Post, Graf, and Ant.
        """
        if full is None:
            self.name = name
            self.post = post
            self.graf = graf
            self.ant = ant

            self.full = round((post + graf + ant) / 3, 2)
        else:
            self.name = name
            self.post, self.graf, self.ant = "N/A", "N/A", "N/A"
            self.full = full

    def dump(self) -> List[Union[str, float]]:
        """
        Dump the values of the metric into a list.

        Useful for writing to CSV.
        """
        return [
            self.name.capitalize(),
            self.post,
            self.graf,
            self.ant,
            self.full,
        ]

    def names(self) -> List[str]:
        """
        Return the names of the values in the metric. (In order)
        """

        return ["Post", "Graf", "Ant", "Full"]
