from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize Firebase
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except:
    print("Firebase not configured - running in local mode")
    db = None

# ═══════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "API is running"})

@app.route("/api/add-child", methods=["POST"])
def add_child():
    """Add new child record"""
    try:
        data = request.json
        child_data = {
            "name": data.get("name"),
            "age_months": data.get("age"),
            "height_cm": data.get("height"),
            "weight_kg": data.get("weight"),
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        if db:
            doc_ref = db.collection("children").add(child_data)
            return jsonify({"success": True, "id": doc_ref[1].id})
        else:
            return jsonify({"success": True, "message": "Child added (local mode)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/get-children", methods=["GET"])
def get_children():
    """Get all children"""
    try:
        if db:
            docs = db.collection("children").stream()
            children = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            return jsonify({"success": True, "data": children})
        else:
            return jsonify({"success": True, "data": []})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/analyze-height", methods=["POST"])
def analyze_height():
    """Analyze height from image"""
    try:
        if "photo" not in request.files:
            return jsonify({"success": False, "error": "No image provided"}), 400
        
        file = request.files["photo"]
        image = Image.open(file.stream)
        
        # Convert to numpy array for OpenCV
        img_array = np.array(image)
        
        # TODO: Add your MediaPipe pose detection here
        # For now, return dummy height
        height_cm = 100.5
        
        # Save to Firebase if child_id provided
        child_id = request.form.get("child_id")
        if child_id and db:
            db.collection("health_records").document(child_id).set({
                "height": height_cm,
                "timestamp": datetime.now().isoformat(),
                "type": "height"
            }, merge=True)
        
        return jsonify({
            "success": True,
            "height_cm": height_cm,
            "confidence": 0.95
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/analyze-anemia", methods=["POST"])
def analyze_anemia():
    """Analyze anemia from eye image"""
    try:
        if "photo" not in request.files:
            return jsonify({"success": False, "error": "No image provided"}), 400
        
        file = request.files["photo"]
        image = Image.open(file.stream)
        img_array = np.array(image)
        
        # TODO: Add your anemia detection model here
        # For now, return dummy risk level
        anemia_risk = "low"  # low, medium, high
        confidence = 0.88
        
        child_id = request.form.get("child_id")
        if child_id and db:
            db.collection("health_records").document(child_id).set({
                "anemia_risk": anemia_risk,
                "timestamp": datetime.now().isoformat(),
                "type": "anemia"
            }, merge=True)
        
        return jsonify({
            "success": True,
            "anemia_risk": anemia_risk,
            "confidence": confidence
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/predict-nutrition", methods=["POST"])
def predict_nutrition():
    """Predict nutrition status"""
    try:
        data = request.json
        height = data.get("height")
        weight = data.get("weight")
        age = data.get("age")
        
        # Simple prediction logic
        bmi = weight / ((height / 100) ** 2)
        
        if bmi < 16:
            status = "red"  # Severe malnutrition
        elif bmi < 18.5:
            status = "yellow"  # Moderate malnutrition
        else:
            status = "green"  # Healthy
        
        return jsonify({
            "success": True,
            "status": status,
            "bmi": round(bmi, 2),
            "message": f"Child is in {status} zone"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/send-sos", methods=["POST"])
def send_sos():
    """Send SOS emergency alert"""
    try:
        data = request.json
        mother_id = data.get("mother_id")
        location = data.get("location")
        
        if db:
            db.collection("sos_alerts").add({
                "mother_id": mother_id,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "status": "active"
            })
        
        # TODO: Send SMS/notification to helpers
        
        return jsonify({
            "success": True,
            "message": "SOS sent! Help is coming!"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ═══════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ═══════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════

if __name__ == "__main__":
    # For local development
    app.run(debug=True, port=5000)
    
    # For production, use gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 api.py
