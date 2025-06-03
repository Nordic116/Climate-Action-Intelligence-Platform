#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE CLIMATE-IQ PLATFORM ANALYSIS
Analyzes all API functionalities, data reliability, and transparency
"""

import sys
import os
import traceback
import time
from datetime import datetime
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.api_handlers.climate_apis import ClimateAPIHandler
from backend.watsonx_integration.watsonx_client import WatsonXClient

class PlatformAnalyzer:
    def __init__(self):
        self.api_handler = ClimateAPIHandler()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'api_status': {},
            'data_quality': {},
            'reliability_scores': {},
            'transparency_report': {},
            'recommendations': []
        }
    
    def analyze_api_functionality(self):
        """Analyze each API's functionality and reliability"""
        print("🔍 ANALYZING API FUNCTIONALITY & RELIABILITY")
        print("=" * 80)
        
        apis_to_test = [
            ('OpenWeather', self._test_openweather),
            ('Carbon Interface', self._test_carbon_interface),
            ('NASA POWER', self._test_nasa_power),
            ('Climate TRACE', self._test_climate_trace),
            ('World Bank', self._test_world_bank),
            ('UN SDG', self._test_un_sdg),
            ('IBM Watson', self._test_watson),
        ]
        
        for api_name, test_func in apis_to_test:
            print(f"\n🔹 Testing {api_name} API")
            print("-" * 50)
            
            try:
                start_time = time.time()
                result = test_func()
                response_time = time.time() - start_time
                
                self.results['api_status'][api_name] = {
                    'status': 'working' if result['success'] else 'error',
                    'response_time': round(response_time, 2),
                    'data_quality': result.get('data_quality', 'unknown'),
                    'reliability': result.get('reliability', 'unknown'),
                    'transparency': result.get('transparency', 'unknown'),
                    'details': result.get('details', {}),
                    'issues': result.get('issues', [])
                }
                
                # Print results
                status_emoji = "✅" if result['success'] else "❌"
                print(f"{status_emoji} Status: {'Working' if result['success'] else 'Error'}")
                print(f"⏱️ Response Time: {response_time:.2f}s")
                print(f"📊 Data Quality: {result.get('data_quality', 'Unknown')}")
                print(f"🔒 Reliability: {result.get('reliability', 'Unknown')}")
                print(f"👁️ Transparency: {result.get('transparency', 'Unknown')}")
                
                if result.get('issues'):
                    print("⚠️ Issues Found:")
                    for issue in result['issues']:
                        print(f"   • {issue}")
                
                if result.get('details'):
                    print("📋 Details:")
                    for key, value in result['details'].items():
                        print(f"   • {key}: {value}")
                        
            except Exception as e:
                print(f"❌ Error testing {api_name}: {str(e)}")
                self.results['api_status'][api_name] = {
                    'status': 'error',
                    'error': str(e),
                    'response_time': None
                }
    
    def _test_openweather(self):
        """Test OpenWeather API functionality"""
        try:
            # Test multiple cities to verify consistency
            test_cities = ['San Francisco', 'New York', 'London', 'Tokyo']
            results = []
            issues = []
            
            for city in test_cities:
                weather = self.api_handler.get_weather_data(city)
                if weather and 'error' not in weather:
                    results.append(weather)
                    
                    # Validate data ranges
                    temp = weather.get('temperature')
                    if temp and (temp < -100 or temp > 60):
                        issues.append(f"Suspicious temperature for {city}: {temp}°C")
                    
                    wind_speed = weather.get('wind_speed')
                    if wind_speed and wind_speed < 0:
                        issues.append(f"Negative wind speed for {city}: {wind_speed}")
                else:
                    issues.append(f"Failed to get weather data for {city}")
            
            success_rate = len(results) / len(test_cities)
            
            return {
                'success': success_rate > 0.5,
                'data_quality': 'High' if success_rate > 0.8 else 'Medium' if success_rate > 0.5 else 'Low',
                'reliability': 'High' if success_rate > 0.8 else 'Medium',
                'transparency': 'High',  # Real-time data with clear source
                'details': {
                    'cities_tested': len(test_cities),
                    'successful_requests': len(results),
                    'success_rate': f"{success_rate:.1%}",
                    'sample_data': results[0] if results else None
                },
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"API connection failed: {str(e)}"]
            }
    
    def _test_carbon_interface(self):
        """Test Carbon Interface API functionality"""
        try:
            # Test different activity types
            test_activities = [
                ('electricity', {'kwh': 100, 'country': 'us'}),
                ('flight', {'departure_airport': 'SFO', 'destination_airport': 'LAX'}),
                ('vehicle', {'distance_km': 100, 'vehicle_make': 'Toyota'})
            ]
            
            results = []
            issues = []
            
            for activity_type, params in test_activities:
                try:
                    result = self.api_handler.calculate_carbon_footprint(activity_type, params)
                    if result and 'error' not in result:
                        results.append(result)
                        
                        # Validate carbon calculations
                        carbon_kg = result.get('carbon_kg')
                        if carbon_kg and carbon_kg < 0:
                            issues.append(f"Negative carbon footprint for {activity_type}: {carbon_kg}")
                        elif carbon_kg and carbon_kg > 10000:  # Suspiciously high
                            issues.append(f"Suspiciously high carbon footprint for {activity_type}: {carbon_kg}")
                    else:
                        issues.append(f"Failed to calculate carbon footprint for {activity_type}")
                except Exception as e:
                    issues.append(f"Error with {activity_type}: {str(e)}")
            
            success_rate = len(results) / len(test_activities)
            
            return {
                'success': success_rate > 0,
                'data_quality': 'High' if success_rate > 0.8 else 'Medium' if success_rate > 0.3 else 'Low',
                'reliability': 'High',  # Consistent calculation methodology
                'transparency': 'High',  # Clear calculation methodology
                'details': {
                    'activities_tested': len(test_activities),
                    'successful_calculations': len(results),
                    'success_rate': f"{success_rate:.1%}",
                    'sample_calculation': results[0] if results else None
                },
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"API connection failed: {str(e)}"]
            }
    
    def _test_nasa_power(self):
        """Test NASA POWER API functionality"""
        try:
            # Test multiple locations
            test_locations = [
                (37.7749, -122.4194),  # San Francisco
                (40.7128, -74.0060),   # New York
                (51.5074, -0.1278),    # London
                (35.6762, 139.6503)    # Tokyo
            ]
            
            results = []
            issues = []
            
            for lat, lon in test_locations:
                try:
                    # Use location string instead of coordinates
                    location_name = f"Location_{lat}_{lon}"
                    data = self.api_handler.get_renewable_energy_potential(location_name)
                    if data and 'error' not in data:
                        results.append(data)
                        
                        # Validate solar irradiance values
                        solar_irradiance = data.get('solar_irradiance')
                        if solar_irradiance and solar_irradiance < 0:
                            issues.append(f"Negative solar irradiance at ({lat}, {lon}): {solar_irradiance}")
                        elif solar_irradiance and solar_irradiance > 15:  # Theoretical maximum ~12-13
                            issues.append(f"Suspiciously high solar irradiance at ({lat}, {lon}): {solar_irradiance}")
                        
                        # Check for missing data indicators
                        if solar_irradiance and abs(solar_irradiance + 999) < 0.1:  # NASA uses -999 for missing data
                            issues.append(f"Missing data indicator found at ({lat}, {lon})")
                    else:
                        issues.append(f"Failed to get renewable energy data for ({lat}, {lon})")
                except Exception as e:
                    issues.append(f"Error with location ({lat}, {lon}): {str(e)}")
            
            success_rate = len(results) / len(test_locations)
            
            return {
                'success': success_rate > 0,
                'data_quality': 'Medium' if len(issues) > 0 else 'High',  # Issues with negative values
                'reliability': 'High',  # NASA is authoritative source
                'transparency': 'High',  # Government data with clear methodology
                'details': {
                    'locations_tested': len(test_locations),
                    'successful_requests': len(results),
                    'success_rate': f"{success_rate:.1%}",
                    'sample_data': results[0] if results else None
                },
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"API connection failed: {str(e)}"]
            }
    
    def _test_climate_trace(self):
        """Test Climate TRACE API functionality"""
        try:
            results = []
            issues = []
            
            # Test sectors endpoint
            try:
                sectors = self.api_handler.get_climate_trace_sectors()
                if sectors and 'sectors' in sectors:
                    results.append(('sectors', sectors))
                    if len(sectors['sectors']) < 5:
                        issues.append("Fewer sectors than expected")
                else:
                    issues.append("Failed to get sectors data")
            except Exception as e:
                issues.append(f"Sectors endpoint error: {str(e)}")
            
            # Test countries endpoint
            try:
                countries = self.api_handler.get_climate_trace_countries()
                if countries:
                    results.append(('countries', countries))
                else:
                    issues.append("Failed to get countries data")
            except Exception as e:
                issues.append(f"Countries endpoint error: {str(e)}")
            
            # Test emissions data
            try:
                emissions = self.api_handler.get_climate_trace_data('USA')
                if emissions:
                    results.append(('emissions', emissions))
                else:
                    issues.append("Failed to get emissions data for USA")
            except Exception as e:
                issues.append(f"Emissions endpoint error: {str(e)}")
            
            success_rate = len(results) / 3  # 3 tests
            
            return {
                'success': success_rate > 0,
                'data_quality': 'Medium',  # API is in development
                'reliability': 'Medium',   # Some endpoints may be unstable
                'transparency': 'High',    # Open climate data initiative
                'details': {
                    'endpoints_tested': 3,
                    'successful_endpoints': len(results),
                    'success_rate': f"{success_rate:.1%}",
                    'available_data': [r[0] for r in results]
                },
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"API connection failed: {str(e)}"]
            }
    
    def _test_world_bank(self):
        """Test World Bank API functionality"""
        try:
            # Test climate indicators for different countries
            test_countries = ['USA', 'CHN', 'DEU', 'JPN']
            indicators = ['EN.ATM.CO2E.PC', 'EG.USE.ELEC.KH.PC']  # CO2 per capita, electricity use
            
            results = []
            issues = []
            
            for country in test_countries:
                for indicator in indicators:
                    try:
                        data = self.api_handler.get_world_bank_data(country, indicator)
                        if data and 'error' not in data:
                            results.append(data)
                            
                            # Validate data ranges
                            if 'value' in data and data['value']:
                                value = float(data['value'])
                                if indicator == 'EN.ATM.CO2E.PC' and (value < 0 or value > 50):
                                    issues.append(f"Suspicious CO2 per capita for {country}: {value}")
                                elif indicator == 'EG.USE.ELEC.KH.PC' and (value < 0 or value > 50000):
                                    issues.append(f"Suspicious electricity use for {country}: {value}")
                        else:
                            issues.append(f"No data for {country} - {indicator}")
                    except Exception as e:
                        issues.append(f"Error with {country} - {indicator}: {str(e)}")
            
            success_rate = len(results) / (len(test_countries) * len(indicators))
            
            return {
                'success': success_rate > 0,
                'data_quality': 'High' if success_rate > 0.7 else 'Medium',
                'reliability': 'High',  # World Bank is authoritative
                'transparency': 'High',  # Government/international organization data
                'details': {
                    'countries_tested': len(test_countries),
                    'indicators_tested': len(indicators),
                    'successful_requests': len(results),
                    'success_rate': f"{success_rate:.1%}",
                    'sample_data': results[0] if results else None
                },
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"API connection failed: {str(e)}"]
            }
    
    def _test_un_sdg(self):
        """Test UN SDG API functionality"""
        try:
            # Test SDG indicators
            results = []
            issues = []
            
            try:
                sdg_data = self.api_handler.get_un_sdg_data()
                if sdg_data and 'error' not in sdg_data:
                    results.append(sdg_data)
                else:
                    issues.append("Failed to get UN SDG data")
            except Exception as e:
                issues.append(f"UN SDG API error: {str(e)}")
            
            success_rate = 1 if results else 0
            
            return {
                'success': success_rate > 0,
                'data_quality': 'High' if success_rate > 0 else 'Unknown',
                'reliability': 'High',  # UN is authoritative source
                'transparency': 'High',  # International organization data
                'details': {
                    'endpoints_tested': 1,
                    'successful_requests': len(results),
                    'success_rate': f"{success_rate:.1%}",
                    'sample_data': results[0] if results else None
                },
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"API connection failed: {str(e)}"]
            }
    
    def _test_watson(self):
        """Test IBM Watson functionality with timeout"""
        try:
            issues = []
            
            # Test with timeout to avoid hanging
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Watson connection timeout")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # 10 second timeout
            
            try:
                watson = WatsonXClient()
                signal.alarm(0)  # Cancel timeout
                
                # Test basic functionality
                if watson.use_fallback:
                    issues.append("Using fallback mode - IBM credentials may be invalid")
                    
                    # Test fallback response
                    response = watson.get_climate_advice("Test query")
                    if response:
                        return {
                            'success': True,
                            'data_quality': 'Medium',  # Fallback data
                            'reliability': 'Medium',   # Not real IBM Watson
                            'transparency': 'High',    # Clearly indicated as fallback
                            'details': {
                                'mode': 'fallback',
                                'response_length': len(response),
                                'sample_response': response[:100] + "..." if len(response) > 100 else response
                            },
                            'issues': issues
                        }
                else:
                    # Test real Watson
                    response = watson.get_climate_advice("What are the main causes of climate change?")
                    if response:
                        return {
                            'success': True,
                            'data_quality': 'High',
                            'reliability': 'High',
                            'transparency': 'High',
                            'details': {
                                'mode': 'direct',
                                'model': watson.model_id,
                                'response_length': len(response),
                                'sample_response': response[:100] + "..." if len(response) > 100 else response
                            },
                            'issues': issues
                        }
                    else:
                        issues.append("Watson returned empty response")
                        
            except TimeoutError:
                signal.alarm(0)
                issues.append("Watson connection timeout - network or credential issue")
                return {
                    'success': False,
                    'data_quality': 'Unknown',
                    'reliability': 'Low',
                    'transparency': 'Medium',
                    'details': {'mode': 'timeout'},
                    'issues': issues
                }
            except Exception as e:
                signal.alarm(0)
                issues.append(f"Watson initialization error: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'issues': issues
                }
            
            return {
                'success': False,
                'issues': ["Unknown Watson error"]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': [f"Watson test failed: {str(e)}"]
            }
    
    def generate_transparency_report(self):
        """Generate comprehensive transparency report"""
        print("\n📋 TRANSPARENCY & DATA SOURCE REPORT")
        print("=" * 80)
        
        transparency_data = {
            'data_sources': {
                'OpenWeather': {
                    'type': 'Real-time weather data',
                    'update_frequency': 'Every 10 minutes',
                    'coverage': 'Global',
                    'reliability': 'High - Commercial weather service',
                    'limitations': 'Point-in-time data, weather forecast accuracy decreases over time'
                },
                'Carbon Interface': {
                    'type': 'Carbon footprint calculations',
                    'methodology': 'EPA emission factors and industry standards',
                    'coverage': 'Global with regional factors',
                    'reliability': 'High - Standardized calculation methods',
                    'limitations': 'Estimates based on averages, actual emissions may vary'
                },
                'NASA POWER': {
                    'type': 'Solar and meteorological data',
                    'methodology': 'Satellite observations and modeling',
                    'coverage': 'Global',
                    'reliability': 'Very High - NASA scientific data',
                    'limitations': 'Modeled data, may not reflect micro-climate conditions'
                },
                'Climate TRACE': {
                    'type': 'Greenhouse gas emissions tracking',
                    'methodology': 'Satellite data, AI analysis, ground truth',
                    'coverage': 'Global facilities and countries',
                    'reliability': 'Medium-High - New initiative, improving',
                    'limitations': 'Beta API, some data gaps, methodology evolving'
                },
                'World Bank': {
                    'type': 'Economic and environmental indicators',
                    'methodology': 'Country reporting and statistical modeling',
                    'coverage': 'Global country-level data',
                    'reliability': 'High - International organization standards',
                    'limitations': 'Annual data, reporting delays, country data quality varies'
                },
                'UN SDG': {
                    'type': 'Sustainable Development Goals indicators',
                    'methodology': 'Country reporting and UN monitoring',
                    'coverage': 'Global country-level progress',
                    'reliability': 'High - UN official data',
                    'limitations': 'Reporting frequency varies, data availability gaps'
                },
                'IBM Watson': {
                    'type': 'AI-generated climate insights',
                    'methodology': 'Large language model trained on diverse data',
                    'coverage': 'General climate knowledge',
                    'reliability': 'Medium - AI-generated content',
                    'limitations': 'May generate plausible but incorrect information, requires verification'
                }
            },
            'fallback_systems': {
                'description': 'When APIs are unavailable, the system uses pre-calculated estimates',
                'data_sources': 'IPCC reports, EPA data, scientific literature',
                'transparency': 'Clearly marked as estimates when fallback is used',
                'limitations': 'Static data, may not reflect current conditions'
            },
            'data_validation': {
                'range_checks': 'Automatic validation of data ranges (e.g., temperature, emissions)',
                'consistency_checks': 'Cross-validation between different data sources',
                'quality_indicators': 'Data quality scores based on source reliability and validation',
                'error_handling': 'Graceful degradation with clear error messages'
            }
        }
        
        self.results['transparency_report'] = transparency_data
        
        # Print summary
        for source, details in transparency_data['data_sources'].items():
            print(f"\n🔹 {source}")
            print(f"   Type: {details['type']}")
            print(f"   Reliability: {details['reliability']}")
            print(f"   Limitations: {details['limitations']}")
    
    def generate_recommendations(self):
        """Generate recommendations for improvement"""
        print("\n💡 RECOMMENDATIONS FOR IMPROVEMENT")
        print("=" * 80)
        
        recommendations = []
        
        # Analyze API status for recommendations
        working_apis = sum(1 for api in self.results['api_status'].values() if api.get('status') == 'working')
        total_apis = len(self.results['api_status'])
        
        if working_apis < total_apis:
            recommendations.append({
                'priority': 'High',
                'category': 'API Reliability',
                'issue': f'Only {working_apis}/{total_apis} APIs are working',
                'recommendation': 'Implement robust fallback systems and API health monitoring'
            })
        
        # Check for data quality issues
        for api_name, api_data in self.results['api_status'].items():
            if api_data.get('issues'):
                recommendations.append({
                    'priority': 'Medium',
                    'category': 'Data Quality',
                    'issue': f'{api_name} has data quality issues',
                    'recommendation': f'Implement data validation and cleaning for {api_name}'
                })
        
        # Watson-specific recommendations
        watson_status = self.results['api_status'].get('IBM Watson', {})
        if watson_status.get('status') != 'working':
            recommendations.append({
                'priority': 'High',
                'category': 'IBM Integration',
                'issue': 'IBM Watson not working properly',
                'recommendation': 'Verify IBM credentials and network connectivity, improve fallback system'
            })
        
        # General recommendations
        recommendations.extend([
            {
                'priority': 'Medium',
                'category': 'User Experience',
                'issue': 'Long response times for some APIs',
                'recommendation': 'Implement caching and background data updates'
            },
            {
                'priority': 'Medium',
                'category': 'Transparency',
                'issue': 'Users may not understand data sources',
                'recommendation': 'Add data source indicators and quality scores to UI'
            },
            {
                'priority': 'Low',
                'category': 'Monitoring',
                'issue': 'No real-time API health monitoring',
                'recommendation': 'Implement dashboard for API status and data quality metrics'
            }
        ])
        
        self.results['recommendations'] = recommendations
        
        # Print recommendations
        for rec in recommendations:
            priority_emoji = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
            print(f"\n{priority_emoji} {rec['priority']} Priority - {rec['category']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Recommendation: {rec['recommendation']}")
    
    def save_report(self):
        """Save comprehensive analysis report"""
        report_file = f"platform_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Full analysis report saved to: {report_file}")
        return report_file

def main():
    print("🔍 CLIMATE-IQ PLATFORM COMPREHENSIVE ANALYSIS")
    print("🤖 Analyzing API functionality, data reliability, and transparency")
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    analyzer = PlatformAnalyzer()
    
    try:
        # Run comprehensive analysis
        analyzer.analyze_api_functionality()
        analyzer.generate_transparency_report()
        analyzer.generate_recommendations()
        
        # Generate summary
        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 80)
        
        working_apis = sum(1 for api in analyzer.results['api_status'].values() 
                          if api.get('status') == 'working')
        total_apis = len(analyzer.results['api_status'])
        
        print(f"✅ Working APIs: {working_apis}/{total_apis}")
        print(f"⚡ Average Response Time: {sum(api.get('response_time', 0) for api in analyzer.results['api_status'].values() if api.get('response_time')) / max(1, sum(1 for api in analyzer.results['api_status'].values() if api.get('response_time'))):.2f}s")
        
        high_quality_apis = sum(1 for api in analyzer.results['api_status'].values() 
                               if api.get('data_quality') == 'High')
        print(f"🏆 High Quality APIs: {high_quality_apis}/{total_apis}")
        
        high_priority_issues = sum(1 for rec in analyzer.results.get('recommendations', []) 
                                  if rec.get('priority') == 'High')
        print(f"🔴 High Priority Issues: {high_priority_issues}")
        
        # Save report
        report_file = analyzer.save_report()
        
        print(f"\n🎯 PLATFORM READINESS: {'READY FOR DEMO' if working_apis >= total_apis * 0.7 else 'NEEDS IMPROVEMENT'}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()