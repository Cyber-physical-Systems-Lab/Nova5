# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 16:00:00 2023
"""
# This script visualizes the emotion ratios from different methods across multiple blocks.
import matplotlib.pyplot as plt
import pandas as pd
# import os
# import numpy as np
# import matplotlib.image as mpimg

# Raw data structured into a nested dictionary format
# Block -> Method -> Emotion -> Ratio
raw_data = {
    "Block 1": {
        "Before cropped": {"angry": 24.73, "disgust": 7.38, "fear": 16.57, "happy": 3.06, "neutral": 36.52, "sad": 9.08, "surprise": 2.67},
        "full with mtcnn": {"angry": 57.10, "fear": 2.81, "happy": 1.02, "neutral": 30.02, "sad": 8.95, "surprise": 0.10},
        "Face cropped exactly": {"angry": 29.18, "disgust": 2.33, "fear": 6.90, "happy": 11.21, "neutral": 2.07, "sad": 48.32},
        "Before cropped mtcnn": {"angry": 54.50, "fear": 2.38, "happy": 0.44, "neutral": 29.05, "sad": 8.27, "surprise": 0.10},
        "cropped with mtcnn": {"angry": 39.41, "disgust": 0.23, "fear": 7.07, "happy": 3.33, "neutral": 6.44, "sad": 22.71},
        "full with yolov8n": {"angry": 35.55, "disgust": 0.17, "fear": 3.64, "happy": 5.95, "neutral": 43.61, "sad": 10.31, "surprise": 0.78},
        "Before cropped with yolov8n": {"angry": 38.24, "disgust": 0.02, "fear": 1.99, "happy": 2.96, "neutral": 44.65, "sad": 9.46, "surprise": 0.85},
        "Cropped with yolov8n": {"angry": 35.21, "disgust": 1.21, "fear": 2.21, "happy": 1.32, "neutral": 1.03, "sad": 26.19, "surprise": 0.03},
    },
    "Block 2": {
        "Before cropped": {"angry": 3.61, "disgust": 0.34, "fear": 5.18, "happy": 17.61, "neutral": 59.67, "sad": 3.99, "surprise": 9.61},
        "Face cropped exactly": {"angry": 18.41, "disgust": 1.73, "fear": 2.10, "happy": 24.89, "neutral": 0.66, "sad": 52.20},
        "full with mtcnn": {"angry": 45.90, "disgust": 0.02, "fear": 0.48, "happy": 3.31, "neutral": 43.48, "sad": 2.18, "surprise": 0.02},
        "Before cropped with mtcnn": {"angry": 36.37, "happy": 3.73, "neutral": 52.26, "sad": 2.42},
        "Cropped with mtcnn": {"angry": 42.12, "disgust": 0.12, "fear": 9.05, "happy": 14.92, "neutral": 6.19, "sad": 13.14},
        "full with yolov8n": {"angry": 10.55, "disgust": 0.12, "fear": 1.23, "happy": 12.27, "neutral": 66.47, "sad": 9.32, "surprise": 0.05},
        "Before cropped with yolov8n": {"angry": 31.36, "disgust": 0.02, "fear": 0.46, "happy": 4.65, "neutral": 57.71, "sad": 4.31, "surprise": 0.02},
        "Cropped with yolov8n": {"angry": 36.70, "disgust": 1.53, "fear": 2.71, "happy": 20.66, "neutral": 1.09, "sad": 37.31},
    },
    "Block 3": {
        "Before cropped": {"angry": 63.20, "disgust": 0.07, "fear": 26.32, "happy": 2.45, "neutral": 5.93, "sad": 1.96, "surprise": 0.07},
        "Face cropped exactly": {"angry": 22.20, "disgust": 0.65, "fear": 6.64, "happy": 11.89, "neutral": 0.43, "sad": 58.03, "surprise": 0.16},
        "full with mtcnn": {"angry": 41.09, "fear": 2.57, "happy": 1.86, "neutral": 46.15, "sad": 7.12, "surprise": 0.07},
        "Before cropped with mtcnn": {"angry": 41.19, "disgust": 0.02, "fear": 2.23, "happy": 1.82, "neutral": 48.52, "sad": 6.13, "surprise": 0.10},
        "Cropped with mtcnn": {"angry": 26.45, "disgust": 0.71, "fear": 4.16, "happy": 11.95, "neutral": 1.58, "sad": 55.05, "surprise": 0.09},
        "full with yolov8n": {"angry": 16.68, "disgust": 0.22, "fear": 1.72, "happy": 10.00, "neutral": 56.61, "sad": 14.62, "surprise": 0.15},
        "Before cropped with yolov8n": {"angry": 37.70, "disgust": 0.10, "fear": 1.23, "happy": 1.14, "neutral": 53.05, "sad": 4.58, "surprise": 0.05},
        "Cropped with yolov8n": {"angry": 26.45, "disgust": 0.71, "fear": 4.16, "happy": 11.95, "neutral": 1.58, "sad": 55.05, "surprise": 0.09},
    },
}


# Plotting setup
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 15))

for idx, (block, methods) in enumerate(raw_data.items()):
    df = pd.DataFrame(methods).T.fillna(0)
    df.plot(kind='bar', stacked=True, ax=axes[idx])
    axes[idx].set_title(f"Emotion Ratios - {block}")
    axes[idx].set_xlabel("Method")
    axes[idx].set_ylabel("Ratio (%)")
    axes[idx].legend(title="Emotion", bbox_to_anchor=(1.02, 1), loc='upper left')

plt.tight_layout()
plt.show()
