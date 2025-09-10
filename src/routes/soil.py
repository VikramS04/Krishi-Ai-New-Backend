from flask import Blueprint, request, jsonify
from src.models.user import db, SoilAnalysis, CropRecommendation
import json
import random
from datetime import datetime

soil_bp = Blueprint('soil', __name__)

@soil_bp.route('/soil/analyze', methods=['POST'])
def analyze_soil():
    """Analyze soil sample and provide recommendations"""
    try:
        data = request.get_json()
        data["ph_level"] = float(data.get("ph_level"))
        data["nitrogen"] = float(data.get("nitrogen"))
        data["phosphorus"] = float(data.get("phosphorus"))
        data["potassium"] = float(data.get("potassium"))
        data["organic_matter"] = float(data.get("organic_matter"))
        data["moisture_content"] = float(data.get("moisture_content"))
        # Validate required fields
        required_fields = ['user_id', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate sample ID
        sample_id = f"SOIL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        # Create soil analysis record
        soil_analysis = SoilAnalysis(
            user_id=data['user_id'],
            sample_id=sample_id,
            location=data.get('location'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            ph_level=data.get('ph_level', round(random.uniform(5.5, 8.5), 1)),
            nitrogen=data.get('nitrogen', round(random.uniform(20, 80), 1)),
            phosphorus=data.get('phosphorus', round(random.uniform(10, 50), 1)),
            potassium=data.get('potassium', round(random.uniform(100, 300), 1)),
            organic_matter=data.get('organic_matter', round(random.uniform(1.5, 4.5), 1)),
            moisture_content=data.get('moisture_content', round(random.uniform(15, 35), 1)),
            electrical_conductivity=data.get('electrical_conductivity', round(random.uniform(0.2, 2.0), 2)),
            soil_type=data.get('soil_type', random.choice(['Loamy', 'Clay', 'Sandy', 'Silty']))
        )
        
        # Calculate health score
        health_score = calculate_soil_health_score(soil_analysis)
        soil_analysis.health_score = health_score
        
        # Generate recommendations
        recommendations = generate_soil_recommendations(soil_analysis)
        soil_analysis.recommendations = json.dumps(recommendations)
        
        # Generate suitable crops
        suitable_crops = generate_suitable_crops(soil_analysis)
        soil_analysis.suitable_crops = json.dumps(suitable_crops)
        
        #db.session.add(soil_analysis)
        #db.session.commit()
        
        return jsonify({
            'success': True,
            'data': soil_analysis.to_dict(),
            'recommendations': recommendations,
            'suitable_crops': suitable_crops
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@soil_bp.route('/soil/history/<int:user_id>', methods=['GET'])
def get_soil_history(user_id):
    """Get soil analysis history for a user"""
    try:
        analyses = SoilAnalysis.query.filter_by(user_id=user_id).order_by(SoilAnalysis.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [analysis.to_dict() for analysis in analyses]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@soil_bp.route('/soil/<int:analysis_id>', methods=['GET'])
def get_soil_analysis(analysis_id):
    """Get specific soil analysis"""
    try:
        analysis = SoilAnalysis.query.get_or_404(analysis_id)
        return jsonify({
            'success': True,
            'data': analysis.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@soil_bp.route('/crops/recommend', methods=['POST'])
def recommend_crops():
    """Recommend crops based on soil analysis and other factors"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get latest soil analysis if soil_analysis_id not provided
        soil_analysis_id = data.get('soil_analysis_id')
        if not soil_analysis_id:
            latest_analysis = SoilAnalysis.query.filter_by(user_id=data['user_id']).order_by(SoilAnalysis.created_at.desc()).first()
            if latest_analysis:
                soil_analysis_id = latest_analysis.id
        
        # Generate crop recommendations
        recommendations = generate_crop_recommendations(data['user_id'], soil_analysis_id, data)
        
        # Save recommendations to database
        for rec in recommendations:
            crop_rec = CropRecommendation(
                user_id=data['user_id'],
                soil_analysis_id=soil_analysis_id,
                crop_name=rec['crop_name'],
                variety=rec.get('variety'),
                confidence_score=rec['confidence_score'],
                expected_yield=rec.get('expected_yield'),
                planting_season=rec.get('planting_season'),
                harvest_time=rec.get('harvest_time'),
                water_requirement=rec.get('water_requirement'),
                fertilizer_recommendation=rec.get('fertilizer_recommendation'),
                pest_management=rec.get('pest_management')
            )
            db.session.add(crop_rec)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': recommendations
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_soil_health_score(soil_analysis):
    """Calculate overall soil health score"""
    score = 0
    factors = 0
    
    # pH score (optimal range 6.0-7.5)
    if soil_analysis.ph_level:
        if 6.0 <= soil_analysis.ph_level <= 7.5:
            score += 25
        elif 5.5 <= soil_analysis.ph_level <= 8.0:
            score += 20
        else:
            score += 10
        factors += 1
    
    # Organic matter score (optimal > 3%)
    if soil_analysis.organic_matter:
        if soil_analysis.organic_matter >= 3.0:
            score += 25
        elif soil_analysis.organic_matter >= 2.0:
            score += 20
        else:
            score += 10
        factors += 1
    
    # NPK balance score
    if soil_analysis.nitrogen and soil_analysis.phosphorus and soil_analysis.potassium:
        npk_score = 0
        if soil_analysis.nitrogen >= 40:
            npk_score += 8
        if soil_analysis.phosphorus >= 25:
            npk_score += 8
        if soil_analysis.potassium >= 150:
            npk_score += 9
        score += npk_score
        factors += 1
    
    # Moisture content score
    if soil_analysis.moisture_content:
        if 20 <= soil_analysis.moisture_content <= 30:
            score += 25
        elif 15 <= soil_analysis.moisture_content <= 35:
            score += 20
        else:
            score += 10
        factors += 1
    
    return round(score / max(factors, 1), 1) if factors > 0 else 50.0

def generate_soil_recommendations(soil_analysis):
    """Generate soil improvement recommendations"""
    recommendations = []
    
    # pH recommendations
    if soil_analysis.ph_level:
        if soil_analysis.ph_level < 6.0:
            recommendations.append({
                'type': 'pH_adjustment',
                'issue': 'Soil is too acidic',
                'recommendation': 'Apply lime to increase pH. Add 2-3 tons of agricultural lime per hectare.',
                'priority': 'high'
            })
        elif soil_analysis.ph_level > 7.5:
            recommendations.append({
                'type': 'pH_adjustment',
                'issue': 'Soil is too alkaline',
                'recommendation': 'Apply sulfur or organic matter to decrease pH. Add 500-1000 kg sulfur per hectare.',
                'priority': 'high'
            })
    
    # Organic matter recommendations
    if soil_analysis.organic_matter and soil_analysis.organic_matter < 2.0:
        recommendations.append({
            'type': 'organic_matter',
            'issue': 'Low organic matter content',
            'recommendation': 'Add compost, farmyard manure, or green manure. Apply 10-15 tons per hectare.',
            'priority': 'medium'
        })
    
    # Nutrient recommendations
    if soil_analysis.nitrogen and soil_analysis.nitrogen < 30:
        recommendations.append({
            'type': 'nitrogen',
            'issue': 'Nitrogen deficiency',
            'recommendation': 'Apply nitrogen-rich fertilizers like urea or ammonium sulfate. Consider legume cover crops.',
            'priority': 'high'
        })
    
    if soil_analysis.phosphorus and soil_analysis.phosphorus < 20:
        recommendations.append({
            'type': 'phosphorus',
            'issue': 'Phosphorus deficiency',
            'recommendation': 'Apply phosphate fertilizers like DAP or rock phosphate.',
            'priority': 'medium'
        })
    
    if soil_analysis.potassium and soil_analysis.potassium < 120:
        recommendations.append({
            'type': 'potassium',
            'issue': 'Potassium deficiency',
            'recommendation': 'Apply potash fertilizers like muriate of potash or sulfate of potash.',
            'priority': 'medium'
        })
    
    return recommendations

def generate_suitable_crops(soil_analysis):
    """Generate list of suitable crops based on soil analysis"""
    crops = []
    
    # Define crop suitability based on soil properties
    crop_database = {
        'Rice': {'ph_range': (5.5, 7.0), 'soil_types': ['Clay', 'Loamy'], 'water_need': 'high'},
        'Wheat': {'ph_range': (6.0, 7.5), 'soil_types': ['Loamy', 'Clay'], 'water_need': 'medium'},
        'Maize': {'ph_range': (5.8, 7.8), 'soil_types': ['Loamy', 'Sandy'], 'water_need': 'medium'},
        'Cotton': {'ph_range': (5.8, 8.0), 'soil_types': ['Loamy', 'Clay'], 'water_need': 'medium'},
        'Sugarcane': {'ph_range': (6.0, 7.5), 'soil_types': ['Loamy', 'Clay'], 'water_need': 'high'},
        'Soybean': {'ph_range': (6.0, 7.0), 'soil_types': ['Loamy', 'Sandy'], 'water_need': 'medium'},
        'Groundnut': {'ph_range': (6.0, 7.0), 'soil_types': ['Sandy', 'Loamy'], 'water_need': 'low'},
        'Tomato': {'ph_range': (6.0, 7.0), 'soil_types': ['Loamy', 'Sandy'], 'water_need': 'medium'},
        'Potato': {'ph_range': (5.0, 6.5), 'soil_types': ['Loamy', 'Sandy'], 'water_need': 'medium'},
        'Onion': {'ph_range': (6.0, 7.5), 'soil_types': ['Loamy', 'Sandy'], 'water_need': 'medium'}
    }
    
    for crop_name, requirements in crop_database.items():
        suitability_score = 0
        
        # Check pH suitability
        if soil_analysis.ph_level:
            ph_min, ph_max = requirements['ph_range']
            if ph_min <= soil_analysis.ph_level <= ph_max:
                suitability_score += 40
            elif ph_min - 0.5 <= soil_analysis.ph_level <= ph_max + 0.5:
                suitability_score += 25
            else:
                suitability_score += 10
        
        # Check soil type suitability
        if soil_analysis.soil_type and soil_analysis.soil_type in requirements['soil_types']:
            suitability_score += 30
        
        # Check nutrient levels
        if soil_analysis.nitrogen and soil_analysis.nitrogen >= 30:
            suitability_score += 10
        if soil_analysis.phosphorus and soil_analysis.phosphorus >= 20:
            suitability_score += 10
        if soil_analysis.potassium and soil_analysis.potassium >= 120:
            suitability_score += 10
        
        if suitability_score >= 50:
            crops.append({
                'crop_name': crop_name,
                'suitability_score': suitability_score,
                'water_requirement': requirements['water_need'],
                'recommended_season': get_recommended_season(crop_name)
            })
    
    # Sort by suitability score
    crops.sort(key=lambda x: x['suitability_score'], reverse=True)
    return crops[:5]  # Return top 5 suitable crops

def generate_crop_recommendations(user_id, soil_analysis_id, data):
    """Generate detailed crop recommendations"""
    recommendations = []
    
    # Sample crop recommendations with detailed information
    sample_crops = [
        {
            'crop_name': 'Rice',
            'variety': 'Basmati 370',
            'confidence_score': 0.85,
            'expected_yield': 4.5,
            'planting_season': 'Kharif',
            'harvest_time': 120,
            'water_requirement': 'High (1500-2000mm)',
            'fertilizer_recommendation': 'NPK 120:60:40 kg/ha',
            'pest_management': 'Monitor for stem borer, leaf folder. Use IPM practices.'
        },
        {
            'crop_name': 'Wheat',
            'variety': 'HD 2967',
            'confidence_score': 0.78,
            'expected_yield': 3.8,
            'planting_season': 'Rabi',
            'harvest_time': 110,
            'water_requirement': 'Medium (450-650mm)',
            'fertilizer_recommendation': 'NPK 150:75:50 kg/ha',
            'pest_management': 'Watch for aphids, rust diseases. Apply fungicides as needed.'
        },
        {
            'crop_name': 'Maize',
            'variety': 'Pioneer 30V92',
            'confidence_score': 0.82,
            'expected_yield': 5.2,
            'planting_season': 'Kharif',
            'harvest_time': 95,
            'water_requirement': 'Medium (500-800mm)',
            'fertilizer_recommendation': 'NPK 180:60:40 kg/ha',
            'pest_management': 'Control fall armyworm, stem borer. Use pheromone traps.'
        }
    ]
    
    return sample_crops

def get_recommended_season(crop_name):
    """Get recommended planting season for crop"""
    seasons = {
        'Rice': 'Kharif (June-July)',
        'Wheat': 'Rabi (November-December)',
        'Maize': 'Kharif (June-July)',
        'Cotton': 'Kharif (April-May)',
        'Sugarcane': 'Spring (February-March)',
        'Soybean': 'Kharif (June-July)',
        'Groundnut': 'Kharif (June-July)',
        'Tomato': 'Winter (October-November)',
        'Potato': 'Rabi (October-November)',
        'Onion': 'Rabi (November-December)'
    }
    return seasons.get(crop_name, 'Consult local expert')

