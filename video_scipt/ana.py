import cv2
from deepface import DeepFace

# Define video paths and configurations
video_configs = [
    {"video_path": "/home/xuezhi/Nova5/video/output1.mp4", "detector_backend": "opencv", "description": "Before cropped", "enforce_detection": False},
    {"video_path": "/home/xuezhi/Nova5/video/face_crop_output1.mp4", "detector_backend": "opencv", "description": "Face cropped exactly", "enforce_detection": False},
    {"video_path": "/home/xuezhi/Nova5/video/input1.mp4", "detector_backend": "mtcnn", "description": "Full with mtcnn", "enforce_detection": True},
    {"video_path": "/home/xuezhi/Nova5/video/output1.mp4", "detector_backend": "mtcnn", "description": "Before cropped with mtcnn", "enforce_detection": True},
    {"video_path": "/home/xuezhi/Nova5/video/face_crop_output1.mp4", "detector_backend": "mtcnn", "description": "Cropped with mtcnn", "enforce_detection": True},
    {"video_path": "/home/xuezhi/Nova5/video/input1.mp4", "detector_backend": "yolov8", "description": "Full with yolov8", "enforce_detection": True},
    {"video_path": "/home/xuezhi/Nova5/video/output1.mp4", "detector_backend": "yolov8", "description": "Before cropped with yolov8", "enforce_detection": True},
    {"video_path": "/home/xuezhi/Nova5/video/face_crop_output1.mp4", "detector_backend": "yolov8", "description": "Cropped with yolov8", "enforce_detection": True},
]

break_all = False  # Set to True to stop processing after the first video

for config in video_configs:
    if break_all:
        break
    
    # Extract video path, detector backend, and description from config
    video_path = config["video_path"]
    print("length of video path:", len(video_path))
    detector_backend = config["detector_backend"]
    description = config["description"]
    enforce_detection = config["enforce_detection"]

    print(f"Processing: {description} (Backend: {detector_backend})")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}.")
        continue

    frame_count = 0
    emodict = dict()

    while cap.isOpened():
        ret, frame = cap.read()
        if break_all:
            break

        if not ret:
            break

        frame_count += 1

        try:
            results = DeepFace.analyze(
                img_path=frame,
                detector_backend=detector_backend,
                actions=['emotion'],
                enforce_detection=enforce_detection,
            )

            # Handle multiple faces
            if isinstance(results, list):
                # Select face closest to the bottom (max y)
                bottom_face = max(results, key=lambda r: r['region']['y'])
            else:
                bottom_face = results

            region = bottom_face['region']
            emotion = bottom_face['dominant_emotion']
            emo = bottom_face['emotion']

            # Draw bounding box and emotion
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(frame, emotion, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)

            if emotion not in emodict:
                emodict[emotion] = 0
            emodict[emotion] += 1

        except Exception as e:
            print(f"Frame {frame_count}: No face detected or error - {e}")

        # Optional: Show frame (press 'q' to stop early)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break_all = True
            break

    print("")
    print(f"Emotion counts for {description}:")
    for emotion in sorted(emodict):  # sort keys alphabetically
        ratio = emodict[emotion] * 1.0 / frame_count * 100
        print(f"{emotion:<10} Frame num: {emodict[emotion]:<5} Ratio: {ratio:.2f}%")

    cap.release()
    cv2.destroyAllWindows()