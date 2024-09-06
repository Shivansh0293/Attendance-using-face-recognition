import cv2
import sqlite3
import datetime

def detect_faces_from_database():
    # Initialize camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Unable to open camera.")
        return

    print("Camera opened successfully.")

    # Load the pre-trained face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Connect to SQLite database
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()

    # Attendance list
    attendance_list = []

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame is read successfully
        if not ret:
            print("Error: Unable to read frame.")
            break

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Draw a rectangle around the detected face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Compare faces from the database
            c.execute("SELECT name, image_path FROM faces")
            records = c.fetchall()
            for record in records:
                name, image_path = record
                
                # Read image
                face_image = cv2.imread(image_path)
                if face_image is None:
                    print(f"Error: Unable to read image from {image_path}")
                    continue

                gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

                # Detect face in the saved face image
                saved_faces = face_cascade.detectMultiScale(gray_face, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                # Check if the detected face matches any saved face
                for (sx, sy, sw, sh) in saved_faces:
                    # Calculate the center of the detected face
                    face_center_x = x + w // 2
                    face_center_y = y + h // 2

                    # Calculate the center of the saved face
                    saved_face_center_x = sx + sw // 2
                    saved_face_center_y = sy + sh // 2

                    # Calculate the distance between the centers of the two faces
                    distance = ((face_center_x - saved_face_center_x) ** 2 + (face_center_y - saved_face_center_y) ** 2) ** 0.5

                    # If the distance is within a certain threshold, consider it a match
                    if distance < 100:
                        # Display the name of the person if recognized
                        cv2.putText(frame, f"Name: {name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        
                        # Add name to attendance list if not already present
                        if name not in attendance_list:
                            attendance_list.append(name)
                        break  # Stop searching for matches once recognized
                else:
                    continue  # Continue searching for matches in the next record

                break  # Stop searching for matches in the next record

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('x') and attendance_list:
            # Record attendance
            record_attendance(attendance_list[0])  # Record attendance for the first person in the list
            attendance_list.clear()                # Clear attendance list after recording
        elif key == ord('q'):
            break

    # Release the camera
    cap.release()

    # Close OpenCV windows
    cv2.destroyAllWindows()

    # Close SQLite connection
    conn.close()

def record_attendance(name):
    # Write attendance 
    with open('attendance.txt', 'a') as f:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Attendance recorded at {current_time}: {name}\n")
    print("Attendance recorded.")

if __name__ == "__main__":
    detect_faces_from_database()