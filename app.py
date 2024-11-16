from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO

# Initialize Flask app
app = Flask(__name__)

# Load the YOLOv8 model
model = YOLO('./model/my_trained_model.pt')

# Open the webcam
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Dictionary to map detected objects to their respective bins
BIN_MAPPING = {
    'plastic-bottle': 'Recycle Bin',
    'glass': 'Recycle Bin',
    'straw': 'Recycle Bin',
    'cardboard': 'Recycle Bin',
    'paper': 'Recycle Bin',
    'apple': 'Waste Bin',
    'orange': 'Waste Bin',
    'battery': 'Hazardous Bin',
    'car battery': 'Hazardous Bin',
    'snack package': 'General Waste Bin'
}

# Define colors for different bins
BIN_COLORS = { #blue green red
    'Recycle Bin': (6, 210, 255),       # Yellow
    'Waste Bin': (0, 255, 0),           # Green
    'Hazardous Bin': (5, 46, 254),       # Red
    'General Waste Bin': (255, 54, 51) # Gray
}

def generate_frames():
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLOv8 detection on the frame with confidence threshold set to 40%
        results = model(frame, conf=0.4)

        # Visualize the results
        annotated_frame = frame.copy()
        for result in results[0].boxes:
            # Get the class ID and confidence score
            class_id = result.cls
            confidence = result.conf
            xyxy = result.xyxy  # Bounding box coordinates

            # Debugging: print xyxy to check its structure
            print("Bounding box (xyxy):", xyxy)

            # Check the type and structure of xyxy
            if len(xyxy) == 1:
                # If it's a single value (e.g., tensor), convert it to a list or array
                xyxy = xyxy[0].tolist()

            # Now, unpack the bounding box coordinates
            x1, y1, x2, y2 = xyxy

            # Get the label based on the class ID (this depends on how YOLO model is trained)
            label = results[0].names[class_id.item()]
            
            # Check the label and map to the appropriate bin
            if label in BIN_MAPPING:
                bin_label = BIN_MAPPING[label]
                bin_color = BIN_COLORS[bin_label]
                
                # Draw a rectangle around the detected object
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), bin_color, 2)
                
                # Add text for bin classification
                font = cv2.FONT_HERSHEY_SIMPLEX
                text_size = cv2.getTextSize(bin_label, font, 0.8, 2)[0]
                text_x = int((x1 + x2 - text_size[0]) / 2)
                text_y = int(y1 - 10)
                
                cv2.putText(annotated_frame, bin_label, (text_x, text_y), font, 0.8, bin_color, 2)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Render the main page
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
