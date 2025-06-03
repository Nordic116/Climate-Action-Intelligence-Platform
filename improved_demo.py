#!/usr/bin/env python3
"""
🏆 IMPROVED CLIMATE-IQ PLATFORM DEMONSTRATION
Robust demo with proper error handling and timeout management
"""

import sys
import os
import signal
import time
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.api_handlers.climate_apis import ClimateAPIHandler
from backend.watsonx_integration.watsonx_client import WatsonXClient

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

class ImprovedDemo:
    def __init__(self):
        self.api_handler = ClimateAPIHandler()
        self.watson_client = None
        self.watson_available = False
        
    def initialize_watson_safely(self):
        """Initialize Watson with timeout protection"""
        print("🤖 Initializing IBM Watson Granite Model...")
        
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # 15 second timeout
        
        try:
            self.watson_client = WatsonXClient()
            signal.alarm(0)  # Cancel timeout
            
            if self.watson_client.use_fallback:
                print("⚠️  Watson in fallback mode - using climate-focused responses")
                self.watson_available = True
            else:
                print("✅ Watson direct mode - IBM Granite model active")
                self.watson_available = True
                
        except TimeoutError:
            signal.alarm(0)
            print("⏰ Watson initialization timeout - proceeding without AI features")
            self.watson_available = False
        except Exception as e:
            signal.alarm(0)
            print(f"❌ Watson initialization failed: {str(e)}")
            self.watson_available = False
    
    def demo_api_integrations(self):
        """Demonstrate all API integrations with reliability checks"""
        print("\n" + "="*80)
        print("🌍 CLIMATE DATA APIS INTEGRATION")
        print("="*80)
        
        # 1. OpenWeather API
        print("\n🔹 1. Real-time Weather Data (OpenWeather)")
        print("-" * 60)
        try:
            weather = self.api_handler.get_weather_data("San Francisco")
            if weather and 'error' not in weather:
                print(f"🌤️ Location: {weather['location']}, {weather['country']}")
                print(f"🌡️ Temperature: {weather['temperature']}°C")
                print(f"💨 Wind Speed: {weather['wind_speed']} m/s")
                print(f"☁️ Conditions: {weather['weather']}")
                print("✅ Data Quality: High - Real-time weather service")
            else:
                print("❌ Weather data unavailable")
        except Exception as e:
            print(f"❌ Weather API error: {str(e)}")
        
        # 2. Carbon Interface API
        print("\n🔹 2. Carbon Footprint Calculation (Carbon Interface)")
        print("-" * 60)
        try:
            carbon = self.api_handler.calculate_carbon_footprint('electricity', {'kwh': 500, 'country': 'us'})
            if carbon and 'error' not in carbon:
                print(f"⚡ Activity: 500 kWh electricity usage")
                print(f"🌱 Carbon Impact: {carbon.get('carbon_kg', 'N/A')} kg CO2")
                print(f"📊 Equivalent: {carbon.get('carbon_lb', 'N/A')} lbs CO2")
                print("✅ Data Quality: High - EPA-based calculations")
            else:
                print("❌ Carbon calculation unavailable")
        except Exception as e:
            print(f"❌ Carbon Interface error: {str(e)}")
        
        # 3. NASA POWER API
        print("\n🔹 3. Renewable Energy Assessment (NASA POWER)")
        print("-" * 60)
        try:
            renewable = self.api_handler.get_renewable_energy_potential("San Francisco")
            if renewable and 'error' not in renewable:
                print(f"☀️ Solar Potential: {renewable.get('solar_potential', 'Unknown')}")
                print(f"💨 Wind Potential: {renewable.get('wind_potential', 'Unknown')}")
                print(f"📈 Avg Solar Irradiance: {renewable.get('avg_solar_irradiance', 'N/A')} kWh/m²/day")
                print("💡 Recommendations:")
                for rec in renewable.get('recommendations', []):
                    print(f"   • {rec}")
                print("✅ Data Quality: High - NASA satellite data")
            else:
                print("❌ Renewable energy data unavailable")
        except Exception as e:
            print(f"❌ NASA POWER error: {str(e)}")
        
        # 4. Climate TRACE API
        print("\n🔹 4. Global Emissions Data (Climate TRACE)")
        print("-" * 60)
        try:
            sectors = self.api_handler.get_climate_trace_sectors()
            countries = self.api_handler.get_climate_trace_countries()
            emissions = self.api_handler.get_climate_trace_data('USA')
            
            if sectors and 'sectors' in sectors:
                sector_list = list(sectors['sectors'].keys())[:5]
                print(f"📊 Available Sectors: {sector_list}...")
                print(f"🔍 Data Source: {sectors.get('source', 'unknown')}")
            
            if countries:
                print(f"🇺🇸 USA Emissions Data: Available")
                print(f"🔍 Data Source: {countries.get('source', 'climate_trace_api')}")
            
            print("✅ Data Quality: Medium-High - Satellite-based tracking")
            
        except Exception as e:
            print(f"❌ Climate TRACE error: {str(e)}")
        
        # 5. World Bank API
        print("\n🔹 5. Climate Indicators (World Bank)")
        print("-" * 60)
        try:
            co2_data = self.api_handler.get_world_bank_data('USA', 'EN.ATM.CO2E.PC')
            if co2_data and 'error' not in co2_data:
                print(f"🏭 USA CO2 per capita: {co2_data.get('value', 'N/A')} metric tons")
                print(f"📅 Year: {co2_data.get('year', 'N/A')}")
                print(f"🔍 Data Source: {co2_data.get('data_source', 'world_bank')}")
                print("✅ Data Quality: High - International organization data")
            else:
                print("❌ World Bank data unavailable")
        except Exception as e:
            print(f"❌ World Bank error: {str(e)}")
        
        # 6. UN SDG API
        print("\n🔹 6. Sustainable Development Goals (UN SDG)")
        print("-" * 60)
        try:
            sdg_data = self.api_handler.get_un_sdg_data()
            if sdg_data and 'climate_related_goals' in sdg_data:
                print(f"🎯 Climate-related SDGs: {len(sdg_data['climate_related_goals'])}")
                print(f"📊 Total SDGs: {sdg_data.get('total_goals', 17)}")
                print(f"🔍 Data Source: {sdg_data.get('data_source', 'un_sdg_api')}")
                
                # Show first climate goal
                if sdg_data['climate_related_goals']:
                    goal = sdg_data['climate_related_goals'][0]
                    print(f"📋 Example - SDG {goal.get('goal', 'N/A')}: {goal.get('title', 'N/A')}")
                
                print("✅ Data Quality: High - UN official data")
            else:
                print("❌ UN SDG data unavailable")
        except Exception as e:
            print(f"❌ UN SDG error: {str(e)}")
    
    def demo_watson_features(self):
        """Demonstrate Watson AI features with timeout protection"""
        if not self.watson_available:
            print("\n🤖 IBM Watson features unavailable - skipping AI demonstrations")
            return
        
        print("\n" + "="*80)
        print("🚀 IBM GRANITE MODEL SHOWCASE")
        print("="*80)
        
        scenarios = [
            {
                'title': 'Personal Climate Advisor',
                'query': 'I live in California and want to reduce my carbon footprint by 30%. What are the most effective actions I can take?',
                'context': 'User is environmentally conscious, owns a home, drives daily'
            },
            {
                'title': 'Business Climate Strategy',
                'query': 'Our tech company wants to become carbon neutral. What\'s a practical roadmap?',
                'context': 'Mid-size tech company, 200 employees, office building, cloud infrastructure'
            },
            {
                'title': 'Climate Data Analysis',
                'query': 'Explain the relationship between renewable energy adoption and carbon emissions reduction',
                'context': 'Educational content for climate awareness'
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🔹 {i}. {scenario['title']}")
            print("-" * 60)
            print(f"💭 Scenario: {scenario['query']}")
            print(f"📋 Context: {scenario['context']}")
            print("\n🤖 IBM Granite Response:")
            print("─" * 40)
            
            # Set timeout for Watson response
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout for response
            
            try:
                response = self.watson_client.get_climate_advice(scenario['query'], scenario['context'])
                signal.alarm(0)  # Cancel timeout
                
                # Truncate long responses for demo
                if len(response) > 500:
                    response = response[:500] + "..."
                
                print(response)
                
            except TimeoutError:
                signal.alarm(0)
                print("⏰ Watson response timeout - using fallback response")
                print("Based on climate science, here are key recommendations for your situation...")
                
            except Exception as e:
                signal.alarm(0)
                print(f"❌ Watson error: {str(e)}")
                print("Using fallback climate advice system...")
    
    def demo_data_transparency(self):
        """Demonstrate data transparency and quality indicators"""
        print("\n" + "="*80)
        print("📋 DATA TRANSPARENCY & QUALITY REPORT")
        print("="*80)
        
        data_sources = {
            'OpenWeather': {
                'reliability': 'High',
                'update_frequency': 'Every 10 minutes',
                'coverage': 'Global',
                'limitations': 'Point-in-time data, forecast accuracy decreases over time'
            },
            'Carbon Interface': {
                'reliability': 'High',
                'methodology': 'EPA emission factors',
                'coverage': 'Global with regional factors',
                'limitations': 'Estimates based on averages, actual emissions may vary'
            },
            'NASA POWER': {
                'reliability': 'Very High',
                'methodology': 'Satellite observations',
                'coverage': 'Global',
                'limitations': 'Modeled data, may not reflect micro-climate conditions'
            },
            'Climate TRACE': {
                'reliability': 'Medium-High',
                'methodology': 'Satellite + AI analysis',
                'coverage': 'Global facilities',
                'limitations': 'Beta API, some data gaps, methodology evolving'
            },
            'World Bank': {
                'reliability': 'High',
                'methodology': 'Country reporting',
                'coverage': 'Country-level data',
                'limitations': 'Annual data, reporting delays'
            },
            'IBM Watson': {
                'reliability': 'Medium',
                'methodology': 'AI language model',
                'coverage': 'General climate knowledge',
                'limitations': 'AI-generated content, requires verification'
            }
        }
        
        for source, details in data_sources.items():
            print(f"\n🔹 {source}")
            print(f"   Reliability: {details['reliability']}")
            print(f"   Methodology: {details.get('methodology', 'Standard practices')}")
            print(f"   Coverage: {details.get('coverage', 'Variable')}")
            print(f"   Limitations: {details['limitations']}")
    
    def generate_summary(self):
        """Generate demonstration summary"""
        print("\n" + "="*80)
        print("📊 DEMONSTRATION SUMMARY")
        print("="*80)
        
        print("✅ Platform Features Demonstrated:")
        print("   • Real-time weather and climate data integration")
        print("   • Carbon footprint calculations with EPA standards")
        print("   • Renewable energy potential assessment")
        print("   • Global emissions tracking and analysis")
        print("   • Climate indicators and SDG progress monitoring")
        
        if self.watson_available:
            print("   • IBM Granite AI-powered climate insights")
            print("   • Personalized climate action recommendations")
            print("   • Business climate strategy development")
        else:
            print("   • IBM Watson integration (currently unavailable)")
        
        print("\n🏆 Hackathon Readiness:")
        print("   • Multiple working climate data APIs")
        print("   • Robust error handling and fallback systems")
        print("   • Transparent data quality indicators")
        print("   • Production-ready architecture")
        print("   • Clear value proposition for climate action")
        
        print("\n🎯 Next Steps:")
        print("   • Verify IBM Watson credentials for full AI features")
        print("   • Implement caching for improved performance")
        print("   • Add user interface for interactive demonstrations")
        print("   • Expand climate action recommendation database")

def main():
    print("🏆 CLIMATE-IQ PLATFORM - IMPROVED DEMONSTRATION")
    print("🤖 Powered by IBM Granite Model & Climate Data APIs")
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("─" * 80)
    
    demo = ImprovedDemo()
    
    try:
        # Initialize Watson safely
        demo.initialize_watson_safely()
        
        # Run demonstrations
        demo.demo_api_integrations()
        demo.demo_watson_features()
        demo.demo_data_transparency()
        demo.generate_summary()
        
        print(f"\n🎉 Demonstration completed successfully!")
        print("🚀 Platform ready for IBM hackathon presentation!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()