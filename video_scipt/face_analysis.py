import cv2
from deepface import DeepFace
import pandas as pd

video_paths = [
    "Block 1.mp4",
    "Block 2.mp4",
    "Block 3.mp4"
]
output_excel_path = "emotion_data.xlsx"  # Path to save the Excel file

# Define crop area
crop_x, crop_y, crop_w, crop_h = 200, 180, 100, 80

def process_video(video_path, crop_x, crop_y, crop_w, crop_h):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}.")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second
    frame_count = 0
    emodict = dict()
    emotion_data = []  # List to store emotions with timestamps

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        timestamp = frame_count / fps  # Calculate timestamp in seconds

        # Crop the frame to the specified area
        cropped_frame = frame[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]

        try:
            results = DeepFace.analyze(
                img_path=cropped_frame,
                detector_backend='mediapipe',
                actions=['emotion'],
                enforce_detection=True,
            )

            # Handle multiple faces
            if isinstance(results, list):
                # Select face closest to the bottom (max y)
                bottom_face = max(results, key=lambda r: r['region']['y'])
            else:
                bottom_face = results
            region = bottom_face['region']
            emotion = bottom_face['emotion']
            emo = bottom_face['dominant_emotion']
            
            
            # Uncomment the line below if you want to see dominant emotions
            # print(f"Detected emotions: {emo}")
            
            # Draw bounding box and emotion
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(cropped_frame, emo, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
            # print(f"Frame {frame_count}: {emotion}")

            if emo not in emodict:
                emodict[emo] = 0
            emodict[emo] += 1

            # Store emotion confidence with timestamp
            emotion_data.append({
                "Frame": frame_count,
                "Timestamp (s)": timestamp,
                "Angry": emotion.get("angry", ""),
                "Disgust": emotion.get("disgust", ""),
                "Fear": emotion.get("fear", ""),
                "Happy": emotion.get("happy", ""),
                "Neutral": emotion.get("neutral", ""),
                "Sad": emotion.get("sad", ""),
                "Surprise": emotion.get("surprise", "")
            })

        except Exception as e:
            # print(f"Frame {frame_count}: No face detected or error - {e}")
            emotion_data.append({
                "Frame": frame_count,
                "Timestamp (s)": timestamp,
                "Angry": "",
                "Disgust": "",
                "Fear": "",
                "Happy": "",
                "Neutral": "",
                "Sad": "",
                "Surprise": ""
            })

        # Optional: Show frame (press 'q' to stop early)
        cv2.imshow('Video', cropped_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Print emotion counts
    print("Emotion counts:")
    for emotion in sorted(emodict):  # sort keys alphabetically
        ratio = emodict[emotion] * 1.0 / frame_count * 100
        print(f"{emotion:<10} Frame num: {emodict[emotion]:<5} Ratio: {ratio:.2f}%")
    print("")

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    return emotion_data

# Process each video and store results in separate DataFrames
dataframes = []
crop_x, crop_y, crop_w, crop_h = 200, 180, 100, 80  # Define crop area
for i, video_path in enumerate(video_paths):
    print(f"Processing video {i + 1}: {video_path}")
    emotion_data = process_video(video_path, crop_x, crop_y, crop_w, crop_h)
    if emotion_data:
        df = pd.DataFrame(emotion_data)
        dataframes.append((f"Block {i + 1}", df))

# Save all DataFrames to an Excel file with different sheets
with pd.ExcelWriter(output_excel_path) as writer:
    for sheet_name, df in dataframes:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Emotion data saved to {output_excel_path}")
