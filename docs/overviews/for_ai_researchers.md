# Retuve for AI Researchers

Retuve works by having a pluggable AI System, that supports multiple different AI Model Modalities. This allows for the AI to be easily swapped out, and for new AI Models to be added with ease.

We Support:

- Segmentation Models
- Landmark Models (Not yet implemented, but theoretically possible with no code changes)
- End-to-End Models (Not yet implemented, but possible with minimal code changes)

This means you can study the performance of new models significantly faster, seeing if your new model achieves better end-results than the current model.

Soon we will have a Benchmarking tool to help you make these comparisons.

## Segmentation Models

Retuve Expects the following parts of a Hip Ultrasound to be segmented:
- Red: Acetabulum and Ilium
- Green: Femoral Head
- Blue: Os Ischium (optional)

<img src="https://github.com/radoss-org/radoss-creative-commons/blob/main/other/ultrasound/172658_14.png?raw=true" alt="drawing" width="250"/><img src="https://github.com/radoss-org/radoss-creative-commons/blob/main/other/ultrasound/172658_14_labels.png?raw=true" alt="drawing" width="250"/>

Attribution of the above Ultrasound Images: Case courtesy of Ryan Thibodeau from https://radiopaedia.org 172658 (https://radiopaedia.org/cases/172658)

To implement your own mode, you can use the following structure:
(A more complete example can be found at https://github.com/radoss-org/retuve/tree/main/examples/ai_plugins/custom_ai_and_config.py)

```python
import my_model

from retuve.classes.seg import SegFrameObjects, SegObject
from retuve.keyphrases.config import Config

# NOTE: Can accept any number of arguments.
def custom_ai_model(dcm, keyphrase, kwarg1, kwarg2) -> List[SegFrameObjects]:
    # Ensures keyphrase is converted to config if its not already
    config = Config.get_config(keyphrase)

    results = my_model.predict(dcm, ...)
    seg_results = []

    # Each result represents results for a single frame.
    for result in results:

        seg_frame_objects = SegFrameObjects(img=result.img)

        # there can be multiple objects in a single frame,
        # even of the same class.
        for box, class_, points, conf, mask in result:

            seg_obj = SegObject(points, class_, mask, box=box, conf=conf)
            seg_frame_objects.append(seg_obj)

        seg_results.append(seg_frame_objects)

    return seg_results


# code to actually use model...
...
```

Where the SegObject instances need to be filled in full:

```python
class HipLabelsUS(Enum):
    """
    Segmentation labels for Hip Ultrasound.
    """

    IlliumAndAcetabulum = 0
    FemoralHead = 1
    OsIchium = 2

class SegObject:
    """
    Class for holding a single segmentation object.
    """

    def __init__(
        self,
        points: List[Tuple[int, int]] = None,
        clss: HipLabelsUS = None,
        mask: NDArrayImg_NxNx3_AllWhite = None,
        conf: float = None,
        box: Tuple[int, int, int, int] = None,
        empty: bool = False,
    ):
    ...
```

## Other Method: Provide Segmentation NIFTIS

Retuve currently does not have a built in AI Model, but we do support running retuve with pre-created NIFTI Masks.

This can be seen in the examples: https://github.com/radoss-org/retuve/tree/main/examples/

**Note that Retuve Trak is not supported with manual NIFTI Masks.**