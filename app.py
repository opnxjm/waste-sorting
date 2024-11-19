from flask import Flask, Response, jsonify, render_template
import cv2
from ultralytics import YOLO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

model = YOLO('./model/latest_model.pt') 
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")

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
    'recyclable': (6, 210, 255),
    'compostable': (0, 255, 0),
    'hazardous': (5, 46, 254), 
    'general': (255, 54, 51),
}

current_bin = "unknown"

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
    global current_bin 

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting...") 
            break 

        print("Sending frame...") 
        
        results = model(frame, conf=0.6)
        current_bin = "unknown"
        

        for result in results[0].boxes:
            class_id = int(result.cls.item())
            xyxy = result.xyxy[0].tolist()
            label = results[0].names[class_id] 

            if label in BIN_MAPPING:
                bin_label = BIN_MAPPING[label] 
                color = BIN_COLORS[bin_label] 

                current_bin = bin_label

                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, bin_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        _, buffer = cv2.imencode('.jpg', frame)
        
        if _:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            print("Failed to encode frame. Continuing...")
            continue

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)