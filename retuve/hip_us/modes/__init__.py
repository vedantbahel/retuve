"""
Contains the code for the two different operation modes of the hip US module:

- Segmentation: For getting landmarks from the segmentation results.
- Landmarks: For getting metrics from the landmarks.

Retuve supports either models that generate segmentaitions or landmarks. The
correct mode(s) will be used based on the model provided.
"""
