from flask import Flask, Response, jsonify, render_template
import cv2
from ultralytics import YOLO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load YOLO model (make sure to use your trained model file)
model = YOLO('./model/my_trained_model.pt')  # or a custom model
cap = cv2.VideoCapture(0)  # Video capture from webcam

if not cap.isOpened():
    print("Error: Could not open webcam.")

# BIN_MAPPING and BIN_COLORS
BIN_MAPPING = {
    "apple": "compostable",
    "banana-peel": "compostable",
    "boots": "general",
    "can": "recyclable",
    "car-battery": "hazardous",
    "cardboard": "recyclable",
    "cylindrical-battery": "hazardous",
    "dented-can": "recyclable",
    "flat-battery": "hazardous",
    "glass-bottle": "recyclable",
    "marker": "general",
    "orange-peel": "compostable",
    "paper": "recyclable",
    "pen": "general",
    "plastic-bags": "recyclable",
    "plastic-bottle": "recyclable",
    "plastic-cup": "recyclable",
    "prismatic-battery": "hazardous",
    "snack-package": "general",
    "straw": "recyclable",  
    "tshirt": "general",
}

BIN_COLORS = {
    'recyclable': (6, 210, 255),  # Yellow
    'compostable': (0, 255, 0),  # Green
    'hazardous': (5, 46, 254),   # Red
    'general': (255, 54, 51)     # Gray
}

# Initialize current_bin as a global variable
current_bin = "unknown"  # Default bin

@app.route('/')
def index():
    """Render the index.html template."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detected_bin')
def detected_bin():
    """Return the detected bin type as JSON."""
    return jsonify(bin_type=current_bin)

def generate_frames():
    """Yield video frames for streaming."""
    global current_bin  # Ensure we are modifying the global variable

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting...")  # Log capture failure
            break  # Optionally, you could also continue if you prefer

        print("Sending frame...")  # Log that the frame is being sent

        # Annotate frame with YOLO results
        results = model(frame, conf=0.6)
        current_bin = "unknown"
        
        # Process each detected object
        for result in results[0].boxes:
            class_id = int(result.cls.item())  # Get class ID
            xyxy = result.xyxy[0].tolist()  # Bounding box coordinates
            label = results[0].names[class_id]  # Get object label (e.g., 'apple')

            # Check if the label exists in BIN_MAPPING
            if label in BIN_MAPPING:
                bin_label = BIN_MAPPING[label]  # Get mapped bin
                color = BIN_COLORS[bin_label]  # Get corresponding color

                # Update the global current_bin variable
                current_bin = bin_label

                # Draw the bounding box and label on the frame
                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, bin_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Encode frame into JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        
        # Ensure successful encoding before yielding the frame
        if _:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            print("Failed to encode frame. Continuing...")  # Log encoding failure
            continue  # Continue to the next iteration if encoding fails

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
