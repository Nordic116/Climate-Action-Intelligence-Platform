"""Climate data service for real-time environmental data integration"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

try:
    import requests
    import aiohttp
except ImportError:
    requests = None
    aiohttp = None

try:
    import pandas as pd
except ImportError:
    pd = None

from config.settings import settings

logger = logging.getLogger(__name__)


class ClimateDataService:
    """Service for fetching and processing climate data from various APIs"""
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = settings.cache_ttl
    
    async def __aenter__(self):
        if aiohttp:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_weather_data(
        self,
        location: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get weather data for a location"""
        
        if not settings.enable_external_apis:
            return self._get_mock_weather_data(location)
        
        # Try OpenWeatherMap first
        if settings.openweather_api_key:
            return await self._get_openweather_data(location, days)
        
        # Fallback to WeatherAPI
        if settings.weatherapi_key:
            return await self._get_weatherapi_data(location, days)
        
        return self._get_mock_weather_data(location)
    
    async def _get_openweather_data(self, location: str, days: int) -> Dict[str, Any]:
        """Fetch data from OpenWeatherMap API"""
        try:
            # Get coordinates first
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                'q': location,
                'limit': 1,
                'appid': settings.openweather_api_key
            }
            
            if self.session:
                async with self.session.get(geocoding_url, params=geocoding_params) as response:
                    geo_data = await response.json()
            else:
                geo_response = requests.get(geocoding_url, params=geocoding_params)
                geo_data = geo_response.json()
            
            if not geo_data:
                return self._get_mock_weather_data(location)
            
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            
            # Get weather data
            weather_url = f"https://api.openweathermap.org/data/2.5/forecast"
            weather_params = {
                'lat': lat,
                'lon': lon,
                'appid': settings.openweather_api_key,
                'units': 'metric'
            }
            
            if self.session:
                async with self.session.get(weather_url, params=weather_params) as response:
                    weather_data = await response.json()
            else:
                weather_response = requests.get(weather_url, params=weather_params)
                weather_data = weather_response.json()
            
            return self._process_openweather_data(weather_data, location)
            
        except Exception as e:
            logger.error(f"Error fetching OpenWeather data: {e}")
            return self._get_mock_weather_data(location)
    
    async def _get_weatherapi_data(self, location: str, days: int) -> Dict[str, Any]:
        """Fetch data from WeatherAPI"""
        try:
            url = f"http://api.weatherapi.com/v1/forecast.json"
            params = {
                'key': settings.weatherapi_key,
                'q': location,
                'days': min(days, 10),  # WeatherAPI free tier limit
                'aqi': 'yes'
            }
            
            if self.session:
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
            else:
                response = requests.get(url, params=params)
                data = response.json()
            
            return self._process_weatherapi_data(data, location)
            
        except Exception as e:
            logger.error(f"Error fetching WeatherAPI data: {e}")
            return self._get_mock_weather_data(location)
    
    def _process_openweather_data(self, data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Process OpenWeatherMap data"""
        try:
            processed = {
                'location': location,
                'source': 'OpenWeatherMap',
                'current': {
                    'temperature': data['list'][0]['main']['temp'],
                    'humidity': data['list'][0]['main']['humidity'],
                    'pressure': data['list'][0]['main']['pressure'],
                    'description': data['list'][0]['weather'][0]['description'],
                    'wind_speed': data['list'][0]['wind']['speed']
                },
                'forecast': []
            }
            
            # Process forecast data
            for item in data['list'][:5]:  # Next 5 periods
                forecast_item = {
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description']
                }
                processed['forecast'].append(forecast_item)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing OpenWeather data: {e}")
            return self._get_mock_weather_data(location)
    
    def _process_weatherapi_data(self, data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Process WeatherAPI data"""
        try:
            current = data['current']
            processed = {
                'location': location,
                'source': 'WeatherAPI',
                'current': {
                    'temperature': current['temp_c'],
                    'humidity': current['humidity'],
                    'pressure': current['pressure_mb'],
                    'description': current['condition']['text'],
                    'wind_speed': current['wind_kph'],
                    'air_quality': current.get('air_quality', {})
                },
                'forecast': []
            }
            
            # Process forecast data
            for day in data['forecast']['forecastday']:
                forecast_item = {
                    'date': day['date'],
                    'max_temp': day['day']['maxtemp_c'],
                    'min_temp': day['day']['mintemp_c'],
                    'humidity': day['day']['avghumidity'],
                    'description': day['day']['condition']['text']
                }
                processed['forecast'].append(forecast_item)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing WeatherAPI data: {e}")
            return self._get_mock_weather_data(location)
    
    def _get_mock_weather_data(self, location: str) -> Dict[str, Any]:
        """Generate mock weather data"""
        return {
            'location': location,
            'source': 'Mock Data',
            'current': {
                'temperature': 22.5,
                'humidity': 65,
                'pressure': 1013.25,
                'description': 'Partly cloudy',
                'wind_speed': 5.2
            },
            'forecast': [
                {
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'max_temp': 25 + i,
                    'min_temp': 15 + i,
                    'humidity': 60 + i * 2,
                    'description': 'Sunny' if i % 2 == 0 else 'Cloudy'
                }
                for i in range(5)
            ]
        }
    
    async def get_air_quality_data(self, location: str) -> Dict[str, Any]:
        """Get air quality data for a location"""
        
        if not settings.enable_external_apis:
            return self._get_mock_air_quality_data(location)
        
        # This would integrate with air quality APIs
        # For now, return mock data
        return self._get_mock_air_quality_data(location)
    
    def _get_mock_air_quality_data(self, location: str) -> Dict[str, Any]:
        """Generate mock air quality data"""
        return {
            'location': location,
            'source': 'Mock Data',
            'aqi': 85,
            'category': 'Moderate',
            'pollutants': {
                'pm2_5': 25.3,
                'pm10': 45.2,
                'no2': 32.1,
                'o3': 78.5,
                'co': 1.2
            },
            'health_recommendations': [
                'Air quality is acceptable for most people',
                'Sensitive individuals should consider limiting outdoor activities'
            ]
        }
    
    async def get_climate_trends(
        self,
        location: str,
        years: int = 10
    ) -> Dict[str, Any]:
        """Get climate trend data"""
        
        if not settings.enable_external_apis:
            return self._get_mock_climate_trends(location, years)
        
        # This would integrate with climate data APIs (NOAA, NASA, etc.)
        return self._get_mock_climate_trends(location, years)
    
    def _get_mock_climate_trends(self, location: str, years: int) -> Dict[str, Any]:
        """Generate mock climate trend data"""
        import random
        
        # Generate mock temperature trends
        base_temp = 15.0
        temp_trends = []
        
        for year in range(datetime.now().year - years, datetime.now().year):
            temp_trends.append({
                'year': year,
                'avg_temperature': base_temp + random.uniform(-2, 3),
                'max_temperature': base_temp + 10 + random.uniform(-3, 5),
                'min_temperature': base_temp - 5 + random.uniform(-3, 3),
                'precipitation': random.uniform(500, 1500)
            })
        
        return {
            'location': location,
            'source': 'Mock Climate Data',
            'period': f'{years} years',
            'temperature_trends': temp_trends,
            'summary': {
                'avg_temp_change': random.uniform(0.5, 2.0),
                'precipitation_change': random.uniform(-10, 15),
                'extreme_events': random.randint(2, 8)
            }
        }
    
    async def get_carbon_data(self, activity_type: str, **kwargs) -> Dict[str, Any]:
        """Get carbon footprint data for activities"""
        
        if not settings.enable_external_apis or not settings.carbon_interface_api_key:
            return self._get_mock_carbon_data(activity_type, **kwargs)
        
        # This would integrate with carbon footprint APIs
        return self._get_mock_carbon_data(activity_type, **kwargs)
    
    def _get_mock_carbon_data(self, activity_type: str, **kwargs) -> Dict[str, Any]:
        """Generate mock carbon footprint data"""
        
        carbon_factors = {
            'electricity': 0.5,  # kg CO2 per kWh
            'gas': 2.3,  # kg CO2 per cubic meter
            'car': 0.2,  # kg CO2 per km
            'flight': 0.25,  # kg CO2 per km
            'train': 0.04,  # kg CO2 per km
        }
        
        factor = carbon_factors.get(activity_type, 0.1)
        amount = kwargs.get('amount', 100)
        
        carbon_footprint = factor * amount
        
        return {
            'activity_type': activity_type,
            'amount': amount,
            'carbon_footprint_kg': carbon_footprint,
            'equivalent_trees': carbon_footprint / 22,  # Trees needed to offset
            'recommendations': [
                f'Consider reducing {activity_type} usage',
                'Look into renewable alternatives',
                'Offset through verified carbon credits'
            ]
        }
    
    async def get_renewable_energy_data(self, location: str) -> Dict[str, Any]:
        """Get renewable energy potential data"""
        
        return {
            'location': location,
            'source': 'Mock Renewable Data',
            'solar_potential': {
                'daily_average_kwh': 4.5,
                'annual_potential_mwh': 1.6,
                'efficiency_rating': 'High'
            },
            'wind_potential': {
                'average_speed_ms': 6.2,
                'capacity_factor': 0.35,
                'suitability': 'Moderate'
            },
            'recommendations': [
                'Solar panels highly recommended',
                'Small wind turbines feasible',
                'Consider hybrid renewable system'
            ]
        }
    
    def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if available and not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return data
            else:
                del self.cache[key]
        return None
    
    def cache_data(self, key: str, data: Dict[str, Any]) -> None:
        """Cache data with timestamp"""
        self.cache[key] = (data, datetime.now())
    
    async def get_comprehensive_climate_report(self, location: str) -> Dict[str, Any]:
        """Get comprehensive climate report for a location"""
        
        # Gather data from multiple sources
        tasks = [
            self.get_weather_data(location),
            self.get_air_quality_data(location),
            self.get_climate_trends(location),
            self.get_renewable_energy_data(location)
        ]
        
        try:
            weather, air_quality, trends, renewable = await asyncio.gather(*tasks)
            
            return {
                'location': location,
                'generated_at': datetime.now().isoformat(),
                'weather': weather,
                'air_quality': air_quality,
                'climate_trends': trends,
                'renewable_energy': renewable,
                'summary': self._generate_climate_summary(weather, air_quality, trends, renewable)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive climate report: {e}")
            return {
                'location': location,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _generate_climate_summary(
        self,
        weather: Dict[str, Any],
        air_quality: Dict[str, Any],
        trends: Dict[str, Any],
        renewable: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary from climate data"""
        
        return {
            'current_conditions': f"Temperature: {weather['current']['temperature']}°C, {weather['current']['description']}",
            'air_quality_status': air_quality['category'],
            'climate_trend': f"Temperature increased by {trends['summary']['avg_temp_change']}°C over past decade",
            'renewable_potential': 'High solar potential, moderate wind potential',
            'recommendations': [
                'Monitor air quality during outdoor activities',
                'Consider renewable energy installation',
                'Prepare for changing climate patterns'
            ]
        }