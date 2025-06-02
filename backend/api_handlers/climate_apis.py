"""
Climate data API integrations
"""
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from config import settings

logger = logging.getLogger(__name__)

class ClimateAPIHandler:
    """Handler for various climate data APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClimateIQ-Platform/1.0'
        })
    
    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get current weather data from OpenWeatherMap"""
        try:
            url = f"{settings.OPENWEATHER_API_BASE}/weather"
            params = {
                'q': location,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {'error': str(e)}
    
    def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get air quality data from OpenWeatherMap"""
        try:
            url = f"{settings.OPENWEATHER_API_BASE}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': settings.OPENWEATHER_API_KEY
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['list']:
                aqi_data = data['list'][0]
                return {
                    'aqi': aqi_data['main']['aqi'],
                    'components': aqi_data['components'],
                    'timestamp': aqi_data['dt']
                }
            
            return {'error': 'No air quality data available'}
            
        except Exception as e:
            logger.error(f"Error fetching air quality data: {e}")
            return {'error': str(e)}
    
    def get_nasa_power_data(self, lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get NASA POWER data for renewable energy potential"""
        try:
            url = f"{settings.NASA_API_BASE}/daily/point"
            params = {
                'parameters': 'ALLSKY_SFC_SW_DWN,T2M,WS10M',  # Solar irradiance, temperature, wind speed
                'community': 'RE',  # Renewable Energy
                'longitude': lon,
                'latitude': lat,
                'start': start_date,
                'end': end_date,
                'format': 'JSON',
                'api_key': settings.NASA_API_KEY
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'solar_irradiance': data['properties']['parameter']['ALLSKY_SFC_SW_DWN'],
                'temperature': data['properties']['parameter']['T2M'],
                'wind_speed': data['properties']['parameter']['WS10M'],
                'location': {
                    'lat': data['geometry']['coordinates'][1],
                    'lon': data['geometry']['coordinates'][0]
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching NASA POWER data: {e}")
            return {'error': str(e)}
    
    def calculate_carbon_footprint(self, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate carbon footprint using Carbon Interface API"""
        try:
            url = f"{settings.CARBON_INTERFACE_API_BASE}/estimates"
            headers = {
                'Authorization': f'Bearer {settings.CARBON_INTERFACE_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Prepare payload based on activity type
            payload = self._prepare_carbon_payload(activity_type, activity_data)
            
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'carbon_kg': data['data']['attributes']['carbon_kg'],
                'carbon_lb': data['data']['attributes']['carbon_lb'],
                'carbon_mt': data['data']['attributes']['carbon_mt'],
                'activity_type': activity_type,
                'activity_data': activity_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating carbon footprint: {e}")
            return {'error': str(e)}
    
    def _prepare_carbon_payload(self, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payload for Carbon Interface API"""
        if activity_type == 'electricity':
            return {
                'type': 'electricity',
                'electricity_unit': 'kwh',
                'electricity_value': activity_data.get('kwh', 0),
                'country': activity_data.get('country', 'us')
            }
        elif activity_type == 'vehicle':
            return {
                'type': 'vehicle',
                'distance_unit': activity_data.get('distance_unit', 'km'),
                'distance_value': activity_data.get('distance', 0),
                'vehicle_model_id': activity_data.get('vehicle_model_id', '7268a9b7-17e8-4c8d-acca-57059252afe9')  # Default car
            }
        elif activity_type == 'flight':
            return {
                'type': 'flight',
                'passengers': activity_data.get('passengers', 1),
                'legs': activity_data.get('legs', [])
            }
        else:
            raise ValueError(f"Unsupported activity type: {activity_type}")
    
    def get_climate_trace_data(self, country: str = None, sector: str = None) -> Dict[str, Any]:
        """Get emissions data from Climate TRACE"""
        try:
            # Note: Climate TRACE API might require different authentication
            # This is a simplified implementation
            url = f"{settings.CLIMATETRACE_API_BASE}/emissions"
            params = {}
            
            if country:
                params['country'] = country
            if sector:
                params['sector'] = sector
            
            # For now, return mock data since Climate TRACE API access might be limited
            return {
                'country': country or 'global',
                'sector': sector or 'all',
                'total_emissions_mt': 50000000,  # Mock data
                'year': 2023,
                'note': 'This is sample data. Real Climate TRACE integration requires proper API access.'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Climate TRACE data: {e}")
            return {'error': str(e)}
    
    def get_world_bank_climate_data(self, country_code: str, indicator: str) -> Dict[str, Any]:
        """Get climate indicators from World Bank API"""
        try:
            url = f"{settings.WORLD_BANK_API_BASE}/country/{country_code}/indicator/{indicator}"
            params = {
                'format': 'json',
                'date': '2020:2023',  # Recent years
                'per_page': 100
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1 and data[1]:
                return {
                    'country': data[1][0]['country']['value'],
                    'indicator': data[1][0]['indicator']['value'],
                    'data': [
                        {
                            'year': item['date'],
                            'value': item['value']
                        }
                        for item in data[1] if item['value'] is not None
                    ]
                }
            
            return {'error': 'No data available'}
            
        except Exception as e:
            logger.error(f"Error fetching World Bank data: {e}")
            return {'error': str(e)}
    
    def get_renewable_energy_potential(self, location: str) -> Dict[str, Any]:
        """Get renewable energy potential for a location"""
        try:
            # Get coordinates from weather API
            weather_data = self.get_weather_data(location)
            if 'error' in weather_data:
                return weather_data
            
            lat = weather_data['coordinates']['lat']
            lon = weather_data['coordinates']['lon']
            
            # Get NASA POWER data for the last 30 days
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            nasa_data = self.get_nasa_power_data(lat, lon, start_date, end_date)
            
            if 'error' in nasa_data:
                return nasa_data
            
            # Calculate averages
            solar_values = list(nasa_data['solar_irradiance'].values())
            wind_values = list(nasa_data['wind_speed'].values())
            
            avg_solar = sum(solar_values) / len(solar_values) if solar_values else 0
            avg_wind = sum(wind_values) / len(wind_values) if wind_values else 0
            
            # Simple potential calculations
            solar_potential = "High" if avg_solar > 5 else "Medium" if avg_solar > 3 else "Low"
            wind_potential = "High" if avg_wind > 6 else "Medium" if avg_wind > 3 else "Low"
            
            return {
                'location': location,
                'solar_potential': solar_potential,
                'wind_potential': wind_potential,
                'avg_solar_irradiance': round(avg_solar, 2),
                'avg_wind_speed': round(avg_wind, 2),
                'recommendations': self._generate_renewable_recommendations(solar_potential, wind_potential)
            }
            
        except Exception as e:
            logger.error(f"Error calculating renewable energy potential: {e}")
            return {'error': str(e)}
    
    def _generate_renewable_recommendations(self, solar_potential: str, wind_potential: str) -> List[str]:
        """Generate renewable energy recommendations"""
        recommendations = []
        
        if solar_potential == "High":
            recommendations.append("Excellent location for solar panels - consider rooftop solar installation")
            recommendations.append("Solar water heating would be very effective in this location")
        elif solar_potential == "Medium":
            recommendations.append("Good solar potential - solar panels would be moderately effective")
        
        if wind_potential == "High":
            recommendations.append("Strong wind resources - consider small wind turbines if permitted")
        elif wind_potential == "Medium":
            recommendations.append("Moderate wind potential - small wind systems might be viable")
        
        if not recommendations:
            recommendations.append("Consider energy efficiency improvements as primary focus")
            recommendations.append("Look into community renewable energy programs")
        
        return recommendations