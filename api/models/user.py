from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    farm_size = db.Column(db.Float, nullable=True)  # in acres
    primary_crops = db.Column(db.Text, nullable=True)  # JSON string
    language_preference = db.Column(db.String(10), default='english')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'location': self.location,
            'farm_size': self.farm_size,
            'primary_crops': self.primary_crops,
            'language_preference': self.language_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SoilAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sample_id = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Soil properties
    ph_level = db.Column(db.Float, nullable=True)
    nitrogen = db.Column(db.Float, nullable=True)
    phosphorus = db.Column(db.Float, nullable=True)
    potassium = db.Column(db.Float, nullable=True)
    organic_matter = db.Column(db.Float, nullable=True)
    moisture_content = db.Column(db.Float, nullable=True)
    electrical_conductivity = db.Column(db.Float, nullable=True)
    soil_type = db.Column(db.String(50), nullable=True)
    
    # Analysis results
    health_score = db.Column(db.Float, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)  # JSON string
    suitable_crops = db.Column(db.Text, nullable=True)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('soil_analyses', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sample_id': self.sample_id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'ph_level': self.ph_level,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'organic_matter': self.organic_matter,
            'moisture_content': self.moisture_content,
            'electrical_conductivity': self.electrical_conductivity,
            'soil_type': self.soil_type,
            'health_score': self.health_score,
            'recommendations': self.recommendations,
            'suitable_crops': self.suitable_crops,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CropRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    soil_analysis_id = db.Column(db.Integer, db.ForeignKey('soil_analysis.id'), nullable=True)
    
    crop_name = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    expected_yield = db.Column(db.Float, nullable=True)
    planting_season = db.Column(db.String(50), nullable=True)
    harvest_time = db.Column(db.Integer, nullable=True)  # days
    
    # Requirements
    water_requirement = db.Column(db.String(50), nullable=True)
    fertilizer_recommendation = db.Column(db.Text, nullable=True)
    pest_management = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('crop_recommendations', lazy=True))
    soil_analysis = db.relationship('SoilAnalysis', backref=db.backref('crop_recommendations', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'soil_analysis_id': self.soil_analysis_id,
            'crop_name': self.crop_name,
            'variety': self.variety,
            'confidence_score': self.confidence_score,
            'expected_yield': self.expected_yield,
            'planting_season': self.planting_season,
            'harvest_time': self.harvest_time,
            'water_requirement': self.water_requirement,
            'fertilizer_recommendation': self.fertilizer_recommendation,
            'pest_management': self.pest_management,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DiseaseDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    crop_type = db.Column(db.String(100), nullable=True)
    
    # Detection results
    disease_name = db.Column(db.String(200), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    severity_level = db.Column(db.String(50), nullable=True)
    affected_area_percentage = db.Column(db.Float, nullable=True)
    
    # Treatment recommendations
    treatment_recommendations = db.Column(db.Text, nullable=True)
    preventive_measures = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('disease_detections', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'crop_type': self.crop_type,
            'disease_name': self.disease_name,
            'confidence_score': self.confidence_score,
            'severity_level': self.severity_level,
            'affected_area_percentage': self.affected_area_percentage,
            'treatment_recommendations': self.treatment_recommendations,
            'preventive_measures': self.preventive_measures,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    rainfall = db.Column(db.Float, nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)
    pressure = db.Column(db.Float, nullable=True)
    
    forecast_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'rainfall': self.rainfall,
            'wind_speed': self.wind_speed,
            'pressure': self.pressure,
            'forecast_date': self.forecast_date.isoformat() if self.forecast_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    language = db.Column(db.String(10), default='english')
    
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('community_posts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'language': self.language,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None
        }

class CommunityComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    post = db.relationship('CommunityPost', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_dict() if self.user else None
        }

