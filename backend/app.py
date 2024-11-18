from flask import Flask, Response, jsonify
from flask_socketio import SocketIO, emit
import cv2
from ultralytics import YOLO
from flask_cors import CORS
import threading

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
CORS(app, origins=["http://localhost:3000"], supports_credentials=True, methods=["GET"])
#CORS(app, origins="*", supports_credentials=True)

# Load the YOLOv8 model
model = YOLO('./model/my_trained_model.pt')

# Open the webcam
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Bin mapping dictionary
BIN_MAPPING = {
    'plastic-bottle': 'recyclable',
    'glass': 'recyclable',
    'straw': 'recyclable',
    'cardboard': 'recyclable',
    'paper': 'recyclable',
    'apple': 'compostable',
    'orange': 'compostable',
    'battery': 'hazardous',
    'car battery': 'hazardous',
    'snack package': 'general'
}

# Define colors for visualization
BIN_COLORS = {
    'recyclable': (6, 210, 255),  # Yellow
    'compostable': (0, 255, 0),  # Green
    'hazardous': (5, 46, 254),   # Red
    'general': (255, 54, 51)     # Gray
}

detected_bin = "unknown"  # Default bin type
frame_lock = threading.Lock()  # Lock to safely share the frame across threads


def detect_objects():
    """Continuously detect objects from the webcam feed."""
    global detected_bin
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Run YOLOv8 detection
        results = model(frame, conf=0.6)

        # Process detections
        for result in results[0].boxes:
            class_id = int(result.cls.item())
            label = results[0].names[class_id]

            # Map label to bin
            if label in BIN_MAPPING:
                detected_bin = BIN_MAPPING[label]
                break


# def generate_frames():
#     """Yield video frames for streaming."""
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to capture frame. Exiting...")  # Log capture failure
#             break  # Optionally, you could also continue if you prefer

#         print("Sending frame...")  # Log that the frame is being sent

#         # Annotate frame with YOLO results
#         results = model(frame, conf=0.6)

#         for result in results[0].boxes:
#             class_id = int(result.cls.item())
#             xyxy = result.xyxy[0].tolist()
#             label = results[0].names[class_id]

#             # Check for recognized label and map to bin
#             if label in BIN_MAPPING:
#                 bin_label = BIN_MAPPING[label]
#                 color = BIN_COLORS[bin_label]

#                 # Draw rectangle and label
#                 x1, y1, x2, y2 = map(int, xyxy)
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                 cv2.putText(frame, bin_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

#         # Encode frame into JPEG
#         _, buffer = cv2.imencode('.jpg', frame)
        
#         # Ensure successful encoding before yielding the frame
#         if _:
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
#         else:
#             print("Failed to encode frame. Continuing...")  # Log encoding failure
#             continue  # Continue to the next iteration if encoding fails

def generate_frames():
    """Yield video frames for streaming."""
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Annotate frame with YOLO results
        results = model(frame, conf=0.6)
        for result in results[0].boxes:
            class_id = int(result.cls.item())
            xyxy = result.xyxy[0].tolist()
            label = results[0].names[class_id]

            if label in BIN_MAPPING:
                bin_label = BIN_MAPPING[label]
                color = BIN_COLORS[bin_label]

                # Draw rectangle and label
                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, bin_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        # Send frame to WebSocket client
        socketio.emit('video_frame', buffer.tobytes())
        print("Sent frame data to client")  # Log that a frame has been sent to the client
        socketio.sleep(0.1)


@app.route('/video_feed')
def video_feed():
    """Video feed route."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detected_bin')
def get_detected_bin():
    """Return the detected bin as JSON."""
    # print(f"Detected bin type: {detected_bin}")
    # print("Received request for detected_bin")
    return jsonify(bin_type=detected_bin)


if __name__ == '__main__':
    # Start the detection thread
    threading.Thread(target=detect_objects, daemon=True).start()

    # Run the Flask app
    # app.run(host="0.0.0.0", port=5001, debug=True)
    socketio.start_background_task(generate_frames)
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)