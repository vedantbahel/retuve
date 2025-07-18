from typing import Iterable, Literal, Tuple

import numpy as np


def extend_line(
    p1: Iterable[float],
    p2: Iterable[float],
    scale: float = 1.2,
    direction: Literal["both", "up", "down"] = "both",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extend the segment (p1, p2) by a multiplicative factor *scale*.

    The mathematics is done only with the vector v = p2 − p1, so the
    result is angle-independent.

    direction
    - "both": grow symmetrically about the midpoint
    - "up"  : grow only at the p1 end
    - "down": grow only at the p2 end
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)

    if scale <= 0:
        raise ValueError("scale must be positive")

    # Treat the two points as a single vector
    v = p2 - p1
    if np.allclose(v, 0):
        raise ValueError("p1 and p2 cannot coincide")

    # Amount of extra length we want, expressed as a vector
    delta = (scale - 1.0) * v

    if direction == "both":
        new_p1 = p1 - 0.5 * delta  # move half of delta backwards
        new_p2 = p2 + 0.5 * delta  # move half of delta forwards
    elif direction == "up":
        new_p1 = p1 - delta  # move the whole delta backwards
        new_p2 = p2  # keep p2 fixed
    elif direction == "down":
        new_p1 = p1  # keep p1 fixed
        new_p2 = p2 + delta  # move the whole delta forwards
    else:
        raise ValueError(f"unknown direction: {direction}")

    return new_p1, new_p2
