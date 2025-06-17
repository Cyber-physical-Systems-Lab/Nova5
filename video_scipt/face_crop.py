# Face Cropping from Video using MTCNN
# This script processes a video file to detect faces using MTCNN and crops the detected faces,
# resizing them to a specified size, and saves the cropped faces into a new video file.
# you need to firstly crop the video by ffmpeg -i input21.mp4 -filter:v "crop=100:80:200:180" -c:a copy output1.mp4
import cv2  # OpenCV for video processing
from facenet_pytorch import MTCNN  # MTCNN for face detection

# Input and output video file paths
input_path = 'output1.mp4'  # Path to the input video file
output_path = 'face_crop_output1.mp4'  # Path to save the output video with cropped faces

# Initialize video capture for reading the input video
cap = cv2.VideoCapture(input_path)

# Initialize MTCNN for face detection
# keep_all=True ensures detection of all faces in a frame
# device='cpu' specifies the computation device
mtcnn = MTCNN(keep_all=True, device='cpu')

# Retrieve video properties
fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second of the input video
width, height = int(cap.get(3)), int(cap.get(4))  # Width and height of the input video frames

# Define output video settings
crop_size = (128, 128)  # Size of the cropped face in the output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for the output video
out = cv2.VideoWriter(output_path, fourcc, fps, crop_size)  # Initialize video writer for output

# Process each frame of the input video
while True:
    ret, frame = cap.read()  # Read a frame from the input video
    if not ret:  # Break the loop if no more frames are available
        break

    # Detect faces in the current frame
    boxes, _ = mtcnn.detect(frame)

    if boxes is not None and len(boxes) > 0:
        # Select the bottom-most face based on vertical position
        target_idx = max(range(len(boxes)), key=lambda i: (boxes[i][1] + boxes[i][3]) / 2)
        x1, y1, x2, y2 = boxes[target_idx].astype(int)  # Extract coordinates of the selected face

        # Clip coordinates to ensure they are within image bounds
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(width, x2); y2 = min(height, y2)

        # Crop the face region from the frame
        face_crop = frame[y1:y2, x1:x2]

        # Resize the cropped face to the defined crop size
        face_resized = cv2.resize(face_crop, crop_size)

        # Write the resized face to the output video
        out.write(face_resized)

# Release resources
cap.release()  # Close the video capture
out.release()  # Close the video writer

# Print confirmation message
print(f"Saved cropped face video to {output_path}")