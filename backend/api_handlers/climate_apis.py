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
    
    def get_climate_trace_data(self, country: str = None, sector: str = None, year: int = 2022) -> Dict[str, Any]:
        """Get emissions data from Climate TRACE using correct API endpoints"""
        try:
            # Use the correct Climate TRACE v6 API endpoints
            if country and sector:
                # Get country emissions for specific sector
                url = f"{settings.CLIMATETRACE_API_BASE}/country/emissions"
                params = {
                    'countries': country.upper(),  # Country codes should be uppercase
                    'sector': sector,
                    'since': year,
                    'to': year
                }
            elif country:
                # Get all emissions for a country
                url = f"{settings.CLIMATETRACE_API_BASE}/country/emissions"
                params = {
                    'countries': country.upper(),
                    'since': year,
                    'to': year
                }
            else:
                # Get asset emissions (sources)
                url = f"{settings.CLIMATETRACE_API_BASE}/assets/emissions"
                params = {
                    'years': str(year),
                    'gas': 'co2e_100yr'  # CO2 equivalent with 100-year warming potential
                }
                if sector:
                    params['sectors'] = sector
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response based on endpoint
            if 'assets/emissions' in url:
                # Asset emissions response
                total_emissions = sum(item.get('Emissions', 0) for item in data if isinstance(item, dict))
                asset_count = sum(item.get('AssetCount', 0) for item in data if isinstance(item, dict))
                
                return {
                    'endpoint': 'assets/emissions',
                    'total_emissions_mt': total_emissions,
                    'asset_count': asset_count,
                    'year': year,
                    'sector': sector or 'all',
                    'gas': 'co2e_100yr',
                    'data': data[:10] if isinstance(data, list) else data  # Limit response size
                }
            else:
                # Country emissions response
                return {
                    'endpoint': 'country/emissions',
                    'country': country,
                    'sector': sector or 'all',
                    'year': year,
                    'data': data[:10] if isinstance(data, list) else data  # Limit response size
                }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Climate TRACE endpoint not found: {e}")
                return self._get_climate_trace_fallback_data(country, sector, year)
            else:
                logger.error(f"HTTP error fetching Climate TRACE data: {e}")
                return {'error': f'HTTP {e.response.status_code}: {str(e)}'}
        except Exception as e:
            logger.error(f"Error fetching Climate TRACE data: {e}")
            return self._get_climate_trace_fallback_data(country, sector, year)
    
    def get_climate_trace_sectors(self) -> Dict[str, Any]:
        """Get available sectors from Climate TRACE"""
        try:
            url = f"{settings.CLIMATETRACE_API_BASE}/definitions/sectors"
            response = self.session.get(url)
            response.raise_for_status()
            
            sectors_data = response.json()
            
            # Convert list to dict if needed
            if isinstance(sectors_data, list):
                sectors_dict = {sector: idx for idx, sector in enumerate(sectors_data)}
            else:
                sectors_dict = sectors_data
            
            return {
                'sectors': sectors_dict,
                'source': 'climate_trace_api'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Climate TRACE sectors: {e}")
            return {
                'sectors': {
                    'power': 1,
                    'transportation': 2,
                    'buildings': 3,
                    'fossil-fuel-operations': 4,
                    'manufacturing': 5,
                    'mineral-extraction': 6,
                    'agriculture': 7,
                    'waste': 8,
                    'fluorinated-gases': 9,
                    'forestry-and-land-use': 10
                },
                'source': 'fallback_data'
            }
    
    def get_climate_trace_countries(self) -> Dict[str, Any]:
        """Get available countries from Climate TRACE"""
        try:
            url = f"{settings.CLIMATETRACE_API_BASE}/definitions/countries"
            response = self.session.get(url)
            response.raise_for_status()
            
            return {
                'countries': response.json(),
                'source': 'climate_trace_api'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Climate TRACE countries: {e}")
            return {
                'countries': ['USA', 'CHN', 'IND', 'RUS', 'JPN', 'DEU', 'IRN', 'SAU', 'KOR', 'CAN'],
                'source': 'fallback_data'
            }
    
    def search_climate_trace_assets(self, country: str = None, sector: str = None, limit: int = 100) -> Dict[str, Any]:
        """Search for emissions sources (assets) in Climate TRACE"""
        try:
            url = f"{settings.CLIMATETRACE_API_BASE}/assets"
            params = {
                'limit': min(limit, 1000),  # API max is 1000
                'year': 2022
            }
            
            if country:
                params['countries'] = country.upper()
            if sector:
                params['sectors'] = sector
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'assets': data,
                'count': len(data) if isinstance(data, list) else 1,
                'filters': {
                    'country': country,
                    'sector': sector,
                    'limit': limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching Climate TRACE assets: {e}")
            return {'error': str(e)}
    
    def _get_climate_trace_fallback_data(self, country: str = None, sector: str = None, year: int = 2022) -> Dict[str, Any]:
        """Provide fallback data when Climate TRACE API is unavailable"""
        # Sample emissions data based on real-world estimates
        fallback_emissions = {
            'USA': {'power': 1500, 'transportation': 1800, 'buildings': 500, 'manufacturing': 400},
            'CHN': {'power': 4000, 'transportation': 800, 'buildings': 300, 'manufacturing': 1200},
            'IND': {'power': 900, 'transportation': 300, 'buildings': 150, 'manufacturing': 600},
            'DEU': {'power': 250, 'transportation': 150, 'buildings': 100, 'manufacturing': 200},
            'JPN': {'power': 350, 'transportation': 200, 'buildings': 80, 'manufacturing': 300}
        }
        
        country_code = country.upper() if country else 'USA'
        country_data = fallback_emissions.get(country_code, fallback_emissions['USA'])
        
        if sector and sector in country_data:
            emissions = country_data[sector]
        else:
            emissions = sum(country_data.values())
        
        return {
            'country': country_code,
            'sector': sector or 'all',
            'total_emissions_mt': emissions,
            'year': year,
            'source': 'fallback_data',
            'note': 'Using estimated data. Climate TRACE API may be temporarily unavailable.'
        }
    
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
            
            # Calculate averages, filtering out NASA missing data indicators (-999)
            solar_values = [v for v in nasa_data['solar_irradiance'].values() if v > -900]
            wind_values = [v for v in nasa_data['wind_speed'].values() if v > -900]
            
            if solar_values and wind_values:
                avg_solar = sum(solar_values) / len(solar_values)
                avg_wind = sum(wind_values) / len(wind_values)
            else:
                # Use fallback estimates if no valid data
                avg_solar = 4.5  # Reasonable global average
                avg_wind = 5.2   # Reasonable global average
            
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
    
    def get_world_bank_data(self, country: str, indicator: str, year: Optional[int] = None) -> Dict[str, Any]:
        """Get World Bank climate and economic indicators"""
        try:
            # World Bank API endpoint
            if year:
                url = f"{settings.WORLD_BANK_API_BASE}/country/{country}/indicator/{indicator}"
                params = {'date': str(year), 'format': 'json'}
            else:
                url = f"{settings.WORLD_BANK_API_BASE}/country/{country}/indicator/{indicator}"
                params = {'date': '2020:2023', 'format': 'json'}  # Last few years
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # World Bank API returns array with metadata and data
            if len(data) > 1 and data[1]:
                latest_data = data[1][0] if data[1] else None
                if latest_data and latest_data.get('value'):
                    return {
                        'country': country,
                        'indicator': indicator,
                        'value': latest_data['value'],
                        'year': latest_data['date'],
                        'country_name': latest_data.get('country', {}).get('value', country),
                        'indicator_name': latest_data.get('indicator', {}).get('value', indicator),
                        'data_source': 'world_bank'
                    }
            
            # Fallback data for common indicators
            fallback_data = self._get_world_bank_fallback(country, indicator)
            return fallback_data
            
        except Exception as e:
            logger.error(f"Error fetching World Bank data: {e}")
            return self._get_world_bank_fallback(country, indicator)
    
    def _get_world_bank_fallback(self, country: str, indicator: str) -> Dict[str, Any]:
        """Provide fallback World Bank data"""
        fallback_values = {
            'EN.ATM.CO2E.PC': {  # CO2 emissions per capita
                'USA': 14.24, 'CHN': 7.38, 'DEU': 8.52, 'JPN': 8.65,
                'IND': 1.91, 'RUS': 11.45, 'GBR': 5.55, 'FRA': 4.27
            },
            'EG.USE.ELEC.KH.PC': {  # Electric power consumption per capita
                'USA': 12154, 'CHN': 4475, 'DEU': 6602, 'JPN': 7820,
                'IND': 805, 'RUS': 6603, 'GBR': 4967, 'FRA': 7245
            }
        }
        
        value = fallback_values.get(indicator, {}).get(country, 0)
        
        return {
            'country': country,
            'indicator': indicator,
            'value': value,
            'year': '2022',
            'data_source': 'fallback_estimate',
            'note': 'Estimated value - API unavailable'
        }
    
    def get_un_sdg_data(self, goal: Optional[int] = None, target: Optional[str] = None) -> Dict[str, Any]:
        """Get UN Sustainable Development Goals data"""
        try:
            # UN SDG API endpoint
            if goal:
                url = f"{settings.UN_SDG_API_BASE}/Goal/{goal}/Target"
            else:
                url = f"{settings.UN_SDG_API_BASE}/Goal"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Process climate-related SDGs
            climate_goals = []
            if isinstance(data, list):
                for item in data:
                    if any(keyword in str(item).lower() for keyword in ['climate', 'energy', 'environment', 'carbon']):
                        climate_goals.append(item)
            
            return {
                'climate_related_goals': climate_goals[:10],  # Limit response
                'total_goals': len(data) if isinstance(data, list) else 1,
                'data_source': 'un_sdg_api'
            }
            
        except Exception as e:
            logger.error(f"Error fetching UN SDG data: {e}")
            return self._get_un_sdg_fallback()
    
    def _get_un_sdg_fallback(self) -> Dict[str, Any]:
        """Provide fallback UN SDG data"""
        return {
            'climate_related_goals': [
                {
                    'goal': 7,
                    'title': 'Affordable and Clean Energy',
                    'description': 'Ensure access to affordable, reliable, sustainable and modern energy for all'
                },
                {
                    'goal': 13,
                    'title': 'Climate Action',
                    'description': 'Take urgent action to combat climate change and its impacts'
                },
                {
                    'goal': 14,
                    'title': 'Life Below Water',
                    'description': 'Conserve and sustainably use the oceans, seas and marine resources'
                },
                {
                    'goal': 15,
                    'title': 'Life on Land',
                    'description': 'Protect, restore and promote sustainable use of terrestrial ecosystems'
                }
            ],
            'total_goals': 17,
            'data_source': 'fallback_data',
            'note': 'Static SDG data - API unavailable'
        }