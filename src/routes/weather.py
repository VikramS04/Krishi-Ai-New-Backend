from flask import Blueprint, request, jsonify
from src.models.user import db, WeatherData
import json
import random
from datetime import datetime, timedelta

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather/current/<location>', methods=['GET'])
def get_current_weather(location):
    """Get current weather for a location"""
    try:
        # Simulate current weather data (in production, integrate with weather API)
        current_weather = simulate_current_weather(location)
        
        # Save to database
        weather_data = WeatherData(
            location=location,
            latitude=current_weather.get('latitude'),
            longitude=current_weather.get('longitude'),
            temperature=current_weather['temperature'],
            humidity=current_weather['humidity'],
            rainfall=current_weather['rainfall'],
            wind_speed=current_weather['wind_speed'],
            pressure=current_weather['pressure'],
            forecast_date=datetime.utcnow()
        )
        
        db.session.add(weather_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': current_weather
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@weather_bp.route('/weather/forecast/<location>', methods=['GET'])
def get_weather_forecast(location):
    """Get weather forecast for a location"""
    try:
        days = request.args.get('days', 7, type=int)
        forecast = simulate_weather_forecast(location, days)
        
        # Save forecast data to database
        for day_forecast in forecast:
            weather_data = WeatherData(
                location=location,
                latitude=day_forecast.get('latitude'),
                longitude=day_forecast.get('longitude'),
                temperature=day_forecast['temperature'],
                humidity=day_forecast['humidity'],
                rainfall=day_forecast['rainfall'],
                wind_speed=day_forecast['wind_speed'],
                pressure=day_forecast['pressure'],
                forecast_date=datetime.strptime(day_forecast['date'], '%Y-%m-%d')
            )
            db.session.add(weather_data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': forecast
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@weather_bp.route('/weather/alerts/<location>', methods=['GET'])
def get_weather_alerts(location):
    """Get weather alerts and farming advisories"""
    try:
        alerts = generate_weather_alerts(location)
        
        return jsonify({
            'success': True,
            'data': alerts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@weather_bp.route('/weather/history/<location>', methods=['GET'])
def get_weather_history(location):
    """Get historical weather data"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        weather_history = WeatherData.query.filter(
            WeatherData.location == location,
            WeatherData.forecast_date >= start_date,
            WeatherData.forecast_date <= end_date
        ).order_by(WeatherData.forecast_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [weather.to_dict() for weather in weather_history]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def simulate_current_weather(location):
    """Simulate current weather data"""
    # Base weather patterns for different regions
    base_temps = {
        'Delhi': 25, 'Mumbai': 28, 'Bangalore': 22, 'Chennai': 30,
        'Kolkata': 27, 'Hyderabad': 26, 'Pune': 24, 'Ahmedabad': 29
    }
    
    base_temp = base_temps.get(location, 25)
    
    # Add seasonal variation
    current_month = datetime.now().month
    if current_month in [12, 1, 2]:  # Winter
        temp_adjustment = -5
    elif current_month in [3, 4, 5]:  # Summer
        temp_adjustment = 8
    elif current_month in [6, 7, 8, 9]:  # Monsoon
        temp_adjustment = -2
    else:  # Post-monsoon
        temp_adjustment = 2
    
    temperature = base_temp + temp_adjustment + random.uniform(-3, 3)
    
    return {
        'location': location,
        'latitude': round(random.uniform(8.0, 35.0), 4),
        'longitude': round(random.uniform(68.0, 97.0), 4),
        'temperature': round(temperature, 1),
        'humidity': round(random.uniform(40, 85), 1),
        'rainfall': round(random.uniform(0, 15), 1),
        'wind_speed': round(random.uniform(5, 25), 1),
        'pressure': round(random.uniform(1000, 1020), 1),
        'condition': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Sunny']),
        'uv_index': random.randint(1, 10),
        'visibility': round(random.uniform(5, 15), 1),
        'timestamp': datetime.utcnow().isoformat()
    }

def simulate_weather_forecast(location, days):
    """Simulate weather forecast for multiple days"""
    forecast = []
    base_weather = simulate_current_weather(location)
    
    for i in range(days):
        forecast_date = datetime.utcnow() + timedelta(days=i)
        
        # Add daily variation
        temp_variation = random.uniform(-4, 4)
        humidity_variation = random.uniform(-10, 10)
        
        day_forecast = {
            'date': forecast_date.strftime('%Y-%m-%d'),
            'location': location,
            'latitude': base_weather['latitude'],
            'longitude': base_weather['longitude'],
            'temperature': round(base_weather['temperature'] + temp_variation, 1),
            'humidity': max(20, min(95, round(base_weather['humidity'] + humidity_variation, 1))),
            'rainfall': round(random.uniform(0, 20), 1),
            'wind_speed': round(random.uniform(5, 30), 1),
            'pressure': round(random.uniform(995, 1025), 1),
            'condition': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Sunny', 'Thunderstorm']),
            'max_temp': round(base_weather['temperature'] + temp_variation + 3, 1),
            'min_temp': round(base_weather['temperature'] + temp_variation - 3, 1),
            'sunrise': '06:30',
            'sunset': '18:45'
        }
        
        forecast.append(day_forecast)
    
    return forecast

def generate_weather_alerts(location):
    """Generate weather alerts and farming advisories"""
    alerts = []
    
    # Simulate different types of alerts
    alert_types = [
        {
            'type': 'Heavy Rainfall',
            'severity': 'High',
            'message': 'Heavy rainfall expected in the next 24-48 hours. Ensure proper drainage in fields.',
            'advisory': 'Postpone spraying operations. Harvest mature crops if possible.',
            'valid_until': (datetime.utcnow() + timedelta(days=2)).isoformat()
        },
        {
            'type': 'High Temperature',
            'severity': 'Medium',
            'message': 'Temperature may rise above 40°C. Heat stress possible for crops.',
            'advisory': 'Increase irrigation frequency. Provide shade for sensitive crops.',
            'valid_until': (datetime.utcnow() + timedelta(days=3)).isoformat()
        },
        {
            'type': 'Frost Warning',
            'severity': 'High',
            'message': 'Frost conditions expected. Protect sensitive crops.',
            'advisory': 'Cover young plants. Use smoke or water spraying to prevent frost damage.',
            'valid_until': (datetime.utcnow() + timedelta(days=1)).isoformat()
        },
        {
            'type': 'Dry Spell',
            'severity': 'Medium',
            'message': 'No rainfall expected for next 10 days.',
            'advisory': 'Plan irrigation schedule. Consider drought-resistant varieties for next season.',
            'valid_until': (datetime.utcnow() + timedelta(days=10)).isoformat()
        }
    ]
    
    # Randomly select 1-2 alerts
    num_alerts = random.randint(0, 2)
    if num_alerts > 0:
        alerts = random.sample(alert_types, num_alerts)
    
    # Add farming advisories based on season
    current_month = datetime.now().month
    seasonal_advisories = get_seasonal_advisories(current_month)
    
    return {
        'alerts': alerts,
        'seasonal_advisories': seasonal_advisories,
        'location': location,
        'generated_at': datetime.utcnow().isoformat()
    }

def get_seasonal_advisories(month):
    """Get seasonal farming advisories"""
    advisories = {
        1: ['Harvest Rabi crops', 'Prepare for summer crops', 'Irrigation management'],
        2: ['Land preparation for summer crops', 'Pruning of fruit trees', 'Pest monitoring'],
        3: ['Sowing of summer crops', 'Fertilizer application', 'Water conservation'],
        4: ['Crop protection measures', 'Harvest planning', 'Market preparation'],
        5: ['Summer crop harvest', 'Monsoon preparation', 'Equipment maintenance'],
        6: ['Kharif sowing', 'Drainage preparation', 'Seed treatment'],
        7: ['Monsoon crop care', 'Pest and disease monitoring', 'Fertilizer application'],
        8: ['Mid-season care', 'Weed management', 'Growth monitoring'],
        9: ['Late Kharif care', 'Harvest preparation', 'Post-harvest planning'],
        10: ['Kharif harvest', 'Rabi preparation', 'Soil testing'],
        11: ['Rabi sowing', 'Winter crop planning', 'Irrigation setup'],
        12: ['Winter crop care', 'Pest management', 'Market planning']
    }
    
    return advisories.get(month, ['General farming activities', 'Crop monitoring', 'Soil health management'])

