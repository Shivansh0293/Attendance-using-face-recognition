import cv2
import sqlite3
import os

def create_database():
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces
                 (name TEXT, image_path TEXT)''')
    conn.commit()
    conn.close()

def save_to_database(name, image_path):
    conn = sqlite3.connect('faces.db')
    c = conn.cursor()
    c.execute("INSERT INTO faces VALUES (?, ?)", (name, image_path))
    conn.commit()
    conn.close()

def main():
    # Create a directory to save face images if it doesn't exist
    if not os.path.exists("faces"):
        os.makedirs("faces")

    cap = cv2.VideoCapture(0)

    create_database() 

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display
        cv2.imshow('frame', frame)

        # Wait for key press
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            # Take pictures from web cam
            ret, frame = cap.read()
            
            # Enter name
            name = input("Enter name: ")

            # Save image to file
            image_path = os.path.join("faces", f"{name}.jpg")
            cv2.imwrite(image_path, frame)

            # Save to database
            save_to_database(name, image_path)
            print(f"Image saved as {image_path}")

        elif key == ord('x'):
            break

    # Release the camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
