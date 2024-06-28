import cv2

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec used to compress the frames
out = cv2.VideoWriter('output.avi', fourcc, 30.0, (1920, 1080))  # Output file, codec, frames per second, and frame size

# Initialize the camera
cap = cv2.VideoCapture(4)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))


if not cap.isOpened():
    print("Error: Cannot open camera.")
else:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Our operations on the frame come here
        # Write the frame into the file 'output.avi'
        out.write(frame)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # Press 'q' to quit the loop
        if cv2.waitKey(1) == ord('q'):
            break

# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()




























