from flask import Blueprint, request, jsonify
from src.models.user import db, DiseaseDetection
import json
import random
from datetime import datetime
import os

disease_bp = Blueprint('disease', __name__)

@disease_bp.route('/disease/detect', methods=['POST'])
def detect_disease():
    """Detect crop disease from uploaded image"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Simulate disease detection (in real implementation, this would use ML models)
        detection_result = simulate_disease_detection(data.get('crop_type', 'Unknown'))
        
        # Create disease detection record
        disease_detection = DiseaseDetection(
            user_id=data['user_id'],
            image_path=data.get('image_path'),
            crop_type=data.get('crop_type'),
            disease_name=detection_result['disease_name'],
            confidence_score=detection_result['confidence_score'],
            severity_level=detection_result['severity_level'],
            affected_area_percentage=detection_result['affected_area_percentage'],
            treatment_recommendations=json.dumps(detection_result['treatment_recommendations']),
            preventive_measures=json.dumps(detection_result['preventive_measures'])
        )
        
        db.session.add(disease_detection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': disease_detection.to_dict(),
            'detection_result': detection_result
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@disease_bp.route('/disease/history/<int:user_id>', methods=['GET'])
def get_disease_history(user_id = 1):
    """Get disease detection history for a user"""
    try:
        detections = DiseaseDetection.query.filter_by(user_id=user_id).order_by(DiseaseDetection.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [detection.to_dict() for detection in detections]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@disease_bp.route('/disease/<int:detection_id>', methods=['GET'])
def get_disease_detection(detection_id):
    """Get specific disease detection"""
    try:
        detection = DiseaseDetection.query.get_or_404(detection_id)
        return jsonify({
            'success': True,
            'data': detection.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@disease_bp.route('/disease/upload', methods=['POST'])
def upload_image():
    """Upload image for disease detection"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file (in production, use cloud storage)
        upload_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"disease_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'image_path': f'/static/uploads/{filename}',
            'message': 'Image uploaded successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def simulate_disease_detection(crop_type):
    """Simulate ML-based disease detection"""
    
    # Disease database with symptoms and treatments
    disease_database = {
        'Rice': [
            {
                'name': 'Blast Disease',
                'symptoms': 'Diamond-shaped lesions on leaves',
                'treatments': ['Apply Tricyclazole fungicide', 'Improve field drainage', 'Use resistant varieties'],
                'prevention': ['Balanced fertilization', 'Avoid excessive nitrogen', 'Proper spacing']
            },
            {
                'name': 'Brown Spot',
                'symptoms': 'Brown spots with yellow halos',
                'treatments': ['Apply Mancozeb fungicide', 'Remove infected debris', 'Improve nutrition'],
                'prevention': ['Seed treatment', 'Balanced NPK', 'Avoid water stress']
            }
        ],
        'Wheat': [
            {
                'name': 'Rust Disease',
                'symptoms': 'Orange-red pustules on leaves',
                'treatments': ['Apply Propiconazole', 'Remove infected plants', 'Use fungicide spray'],
                'prevention': ['Use resistant varieties', 'Proper sowing time', 'Avoid dense planting']
            },
            {
                'name': 'Powdery Mildew',
                'symptoms': 'White powdery growth on leaves',
                'treatments': ['Apply sulfur-based fungicide', 'Improve air circulation', 'Remove infected parts'],
                'prevention': ['Avoid overhead irrigation', 'Proper spacing', 'Resistant varieties']
            }
        ],
        'Tomato': [
            {
                'name': 'Late Blight',
                'symptoms': 'Dark lesions on leaves and fruits',
                'treatments': ['Apply Metalaxyl fungicide', 'Remove infected plants', 'Improve drainage'],
                'prevention': ['Avoid overhead watering', 'Good air circulation', 'Crop rotation']
            },
            {
                'name': 'Early Blight',
                'symptoms': 'Concentric rings on older leaves',
                'treatments': ['Apply Chlorothalonil', 'Remove lower leaves', 'Mulching'],
                'prevention': ['Proper spacing', 'Avoid water stress', 'Balanced nutrition']
            }
        ]
    }
    
    # Get diseases for the crop type
    crop_diseases = disease_database.get(crop_type, disease_database['Tomato'])
    selected_disease = random.choice(crop_diseases)
    
    # Generate detection result
    confidence_score = round(random.uniform(0.75, 0.95), 2)
    severity_levels = ['Mild', 'Moderate', 'Severe']
    severity = random.choice(severity_levels)
    affected_percentage = round(random.uniform(5, 40), 1)
    
    return {
        'disease_name': selected_disease['name'],
        'confidence_score': confidence_score,
        'severity_level': severity,
        'affected_area_percentage': affected_percentage,
        'symptoms': selected_disease['symptoms'],
        'treatment_recommendations': selected_disease['treatments'],
        'preventive_measures': selected_disease['prevention']
    }

