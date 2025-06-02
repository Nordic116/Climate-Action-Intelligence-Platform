"""
Main Streamlit application for Climate Action Intelligence Platform
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rag_system.climate_rag import ClimateRAGSystem
from backend.api_handlers.climate_apis import ClimateAPIHandler
from backend.data_processors.impact_tracker import ImpactTracker
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ClimateIQ - AI Climate Action Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #228B22);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f8f0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #228B22;
        margin: 0.5rem 0;
    }
    .action-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_systems():
    """Initialize backend systems"""
    try:
        rag_system = ClimateRAGSystem()
        rag_system.initialize_with_sample_data()
        
        api_handler = ClimateAPIHandler()
        impact_tracker = ImpactTracker()
        
        return rag_system, api_handler, impact_tracker
    except Exception as e:
        st.error(f"Error initializing systems: {e}")
        st.error("Failed to initialize backend systems. Please check your configuration.")
        # Return mock objects for demonstration
        return None, None, None

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 ClimateIQ - Your AI Climate Action Partner</h1>
        <p>Personalized climate solutions powered by IBM watsonx.ai and real-time data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize systems
    rag_system, api_handler, impact_tracker = initialize_systems()
    
    # Check if systems initialized properly
    demo_mode = not all([rag_system, api_handler, impact_tracker])
    if demo_mode:
        st.warning("⚠️ Running in demonstration mode. Some features may be limited.")
        st.info("💡 This demo showcases the platform's interface and capabilities. Full functionality requires proper API configuration.")
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 Your Profile")
        
        # User identification
        user_id = st.text_input("User ID", value="demo_user", help="Enter a unique identifier")
        
        # Location and basic info
        location = st.text_input("📍 Location", value="New York, NY", help="Enter your city, state/country")
        lifestyle = st.selectbox("🏠 Lifestyle", ["Urban", "Suburban", "Rural"])
        household_size = st.number_input("👥 Household Size", min_value=1, max_value=10, value=2)
        
        # Interests and goals
        st.subheader("🎯 Climate Goals")
        interests = st.multiselect(
            "Areas of Interest",
            ["Energy Efficiency", "Renewable Energy", "Transportation", "Food & Diet", "Waste Reduction", "Water Conservation"],
            default=["Energy Efficiency", "Transportation"]
        )
        
        budget = st.selectbox("💰 Budget for Climate Actions", ["Low ($0-500)", "Medium ($500-2000)", "High ($2000+)"])
        
        # Current actions
        current_actions = st.text_area("Current Climate Actions", 
                                     placeholder="Describe any climate actions you're already taking...")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Action Plan", "📊 Impact Tracker", "🌤️ Local Data", "💬 AI Assistant", "🏆 Community"])
    
    # User profile dictionary
    user_profile = {
        'user_id': user_id,
        'location': location,
        'lifestyle': lifestyle,
        'household_size': household_size,
        'interests': interests,
        'budget': budget,
        'current_actions': current_actions
    }
    
    with tab1:
        display_action_plan(rag_system, user_profile, demo_mode)
    
    with tab2:
        display_impact_tracker(impact_tracker, user_id, demo_mode)
    
    with tab3:
        display_local_data(api_handler, location, demo_mode)
    
    with tab4:
        display_ai_assistant(rag_system, user_profile, demo_mode)
    
    with tab5:
        display_community(impact_tracker, demo_mode)

def display_action_plan(rag_system, user_profile, demo_mode=False):
    """Display personalized action plan"""
    st.header("🎯 Your Personalized Climate Action Plan")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate New Action Plan", type="primary"):
            with st.spinner("🤖 Analyzing your profile and generating personalized recommendations..."):
                if demo_mode or not rag_system:
                    # Demo mode action plan
                    st.success("✅ Your personalized action plan is ready!")
                    st.markdown("### 📋 Recommended Actions")
                    demo_plan = f"""
                    **Personalized for {user_profile['location']} - {user_profile['lifestyle']} Lifestyle**
                    
                    **🏠 Home Energy (Priority: High)**
                    - Switch to LED lighting (saves 75% energy)
                    - Install programmable thermostat (saves 10-15% on heating/cooling)
                    - Improve insulation and seal air leaks
                    
                    **🚗 Transportation (Priority: High)**
                    - Walk/bike for trips under 2 miles
                    - Use public transportation when available
                    - Consider carpooling for longer commutes
                    
                    **🍽️ Food & Consumption (Priority: Medium)**
                    - Reduce meat consumption by 2-3 days per week
                    - Buy local and seasonal produce
                    - Minimize food waste through meal planning
                    
                    **💧 Water Conservation (Priority: Medium)**
                    - Install low-flow showerheads and faucets
                    - Fix leaks promptly
                    - Collect rainwater for gardening
                    
                    **Estimated Annual Impact:** 2.5 tons CO2 reduction, $800 savings
                    """
                    st.markdown(demo_plan)
                    st.info("💡 This is a demo action plan. Full personalization requires proper API configuration.")
                else:
                    try:
                        # Generate personalized plan using RAG system
                        query = f"Create a personalized climate action plan for someone in {user_profile['location']} with {user_profile['lifestyle']} lifestyle, household of {user_profile['household_size']}, interested in {', '.join(user_profile['interests'])}, with {user_profile['budget']} budget."
                        
                        response, sources = rag_system.retrieve_and_generate(query, user_profile)
                        
                        st.success("✅ Your personalized action plan is ready!")
                        
                        # Display the plan
                        st.markdown("### 📋 Recommended Actions")
                        st.markdown(response)
                        
                        # Display sources
                        if sources:
                            with st.expander("📚 Supporting Information Sources"):
                                for i, source in enumerate(sources[:3]):
                                    st.write(f"**Source {i+1}:** {source['metadata'].get('title', 'Climate Data')}")
                                    st.write(f"*Category:* {source['metadata'].get('category', 'General')}")
                                    st.write(f"*Relevance:* {source['similarity']:.2%}")
                                    st.write("---")
                    
                    except Exception as e:
                        st.error(f"Error generating action plan: {e}")
    
    with col2:
        st.markdown("### 💡 Quick Tips")
        st.info("💡 **Pro Tip:** The more specific your location and interests, the better your personalized recommendations!")
        
        st.markdown("### 🎯 Focus Areas")
        for interest in user_profile['interests']:
            st.markdown(f"• {interest}")

def display_impact_tracker(impact_tracker, user_id, demo_mode=False):
    """Display impact tracking dashboard"""
    st.header("📊 Your Environmental Impact")
    
    # Get user impact summary
    impact_summary = impact_tracker.get_user_impact_summary(user_id, days=30)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌱 Carbon Saved",
            f"{impact_summary['total_carbon_saved_kg']:.1f} kg",
            help="Total CO2 emissions prevented"
        )
    
    with col2:
        st.metric(
            "⚡ Energy Saved",
            f"{impact_summary['total_energy_saved_kwh']:.1f} kWh",
            help="Total energy consumption reduced"
        )
    
    with col3:
        st.metric(
            "💧 Water Saved",
            f"{impact_summary['total_water_saved_liters']:.0f} L",
            help="Total water consumption reduced"
        )
    
    with col4:
        st.metric(
            "💰 Cost Savings",
            f"${impact_summary['total_cost_savings']:.2f}",
            help="Estimated cost savings"
        )
    
    # Action logging
    st.subheader("➕ Log New Climate Action")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        action_type = st.selectbox(
            "Action Category",
            ["energy_efficiency", "transportation", "renewable_energy", "food", "water", "waste"]
        )
        
        action_subtype = st.selectbox(
            "Specific Action",
            get_action_subtypes(action_type)
        )
        
        description = st.text_input("Description", placeholder="Describe your climate action...")
        quantity = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.1)
        unit = st.text_input("Unit", value="unit")
    
    with col2:
        st.markdown("### 📝 Action Examples")
        examples = get_action_examples(action_type)
        for example in examples:
            st.write(f"• {example}")
    
    if st.button("📝 Log Action"):
        if description:
            try:
                action_data = {
                    'action_type': action_type,
                    'subtype': action_subtype,
                    'description': description,
                    'quantity': quantity,
                    'unit': unit,
                    'location': user_id  # Using user_id as location for demo
                }
                
                record = impact_tracker.track_action(user_id, action_data)
                st.success(f"✅ Action logged! Estimated impact: {record.carbon_saved_kg:.2f} kg CO2 saved")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error logging action: {e}")
        else:
            st.warning("Please provide a description for your action.")
    
    # Recent actions
    if impact_summary['recent_actions']:
        st.subheader("📋 Recent Actions")
        for action in reversed(impact_summary['recent_actions']):
            with st.expander(f"{action['description']} - {action['timestamp'][:10]}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Carbon Saved:** {action['carbon_saved_kg']:.2f} kg")
                with col2:
                    st.write(f"**Energy Saved:** {action['energy_saved_kwh']:.2f} kWh")
                with col3:
                    st.write(f"**Cost Savings:** ${action['cost_savings']:.2f}")
    
    # Equivalent metrics
    if impact_summary['equivalent_metrics']:
        st.subheader("🌳 Impact Equivalents")
        equivalents = impact_summary['equivalent_metrics']
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🌳 **Trees Planted:** {equivalents.get('trees_planted_equivalent', 0)} trees")
            st.info(f"🚗 **Miles Not Driven:** {equivalents.get('miles_not_driven', 0)} miles")
        
        with col2:
            st.info(f"⛽ **Gasoline Saved:** {equivalents.get('gasoline_not_used_liters', 0)} liters")
            st.info(f"🔥 **Coal Not Burned:** {equivalents.get('coal_not_burned_kg', 0)} kg")

def display_local_data(api_handler, location, demo_mode=False):
    """Display local climate and environmental data"""
    st.header("🌤️ Local Climate Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌡️ Current Weather")
        if st.button("🔄 Refresh Weather Data"):
            with st.spinner("Fetching weather data..."):
                weather_data = api_handler.get_weather_data(location)
                
                if 'error' not in weather_data:
                    st.success(f"📍 **{weather_data['location']}, {weather_data['country']}**")
                    
                    # Weather metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("🌡️ Temperature", f"{weather_data['temperature']:.1f}°C")
                    with col_b:
                        st.metric("💨 Wind Speed", f"{weather_data['wind_speed']:.1f} m/s")
                    with col_c:
                        st.metric("💧 Humidity", f"{weather_data['humidity']}%")
                    
                    st.write(f"**Conditions:** {weather_data['weather'].title()}")
                    
                    # Air quality
                    lat, lon = weather_data['coordinates']['lat'], weather_data['coordinates']['lon']
                    air_quality = api_handler.get_air_quality(lat, lon)
                    
                    if 'error' not in air_quality:
                        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
                        aqi_colors = {1: "green", 2: "lightgreen", 3: "yellow", 4: "orange", 5: "red"}
                        
                        aqi = air_quality['aqi']
                        st.markdown(f"**Air Quality:** <span style='color: {aqi_colors[aqi]}'>{aqi_levels[aqi]} (AQI: {aqi})</span>", 
                                  unsafe_allow_html=True)
                else:
                    st.error(f"Error fetching weather data: {weather_data['error']}")
    
    with col2:
        st.subheader("🔋 Renewable Energy Potential")
        if st.button("🔄 Analyze Renewable Potential"):
            with st.spinner("Analyzing renewable energy potential..."):
                renewable_data = api_handler.get_renewable_energy_potential(location)
                
                if 'error' not in renewable_data:
                    st.success(f"📍 **Analysis for {renewable_data['location']}**")
                    
                    # Potential metrics
                    col_a, col_b = st.columns(2)
                    with col_a:
                        solar_color = {"High": "green", "Medium": "orange", "Low": "red"}[renewable_data['solar_potential']]
                        st.markdown(f"**☀️ Solar Potential:** <span style='color: {solar_color}'>{renewable_data['solar_potential']}</span>", 
                                  unsafe_allow_html=True)
                        st.write(f"Avg. Solar Irradiance: {renewable_data['avg_solar_irradiance']} kWh/m²/day")
                    
                    with col_b:
                        wind_color = {"High": "green", "Medium": "orange", "Low": "red"}[renewable_data['wind_potential']]
                        st.markdown(f"**💨 Wind Potential:** <span style='color: {wind_color}'>{renewable_data['wind_potential']}</span>", 
                                  unsafe_allow_html=True)
                        st.write(f"Avg. Wind Speed: {renewable_data['avg_wind_speed']} m/s")
                    
                    # Recommendations
                    st.markdown("**🎯 Recommendations:**")
                    for rec in renewable_data['recommendations']:
                        st.write(f"• {rec}")
                else:
                    st.error(f"Error analyzing renewable potential: {renewable_data['error']}")
    
    # Carbon footprint calculator
    st.subheader("🧮 Carbon Footprint Calculator")
    
    calc_type = st.selectbox("Calculate emissions for:", ["Electricity Usage", "Vehicle Travel", "Flight"])
    
    if calc_type == "Electricity Usage":
        kwh = st.number_input("Electricity usage (kWh)", min_value=0.0, value=100.0)
        country = st.selectbox("Country", ["us", "ca", "gb", "de", "fr", "au"])
        
        if st.button("Calculate Electricity Emissions"):
            activity_data = {"kwh": kwh, "country": country}
            result = api_handler.calculate_carbon_footprint("electricity", activity_data)
            
            if 'error' not in result:
                st.success(f"🌱 **Carbon Footprint:** {result['carbon_kg']:.2f} kg CO2")
                st.info(f"💡 **Tip:** This is equivalent to driving {result['carbon_kg']/0.404:.1f} miles in an average car")
            else:
                st.error(f"Error calculating emissions: {result['error']}")

def display_ai_assistant(rag_system, user_profile, demo_mode=False):
    """Display AI assistant chat interface"""
    st.header("💬 AI Climate Assistant")
    
    st.markdown("Ask me anything about climate action, sustainability, or environmental impact!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI climate assistant. How can I help you take action against climate change today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about climate action..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if demo_mode or not rag_system:
                    # Demo mode responses
                    demo_responses = {
                        "energy": "Here are some energy-saving tips: 1) Switch to LED bulbs, 2) Use programmable thermostats, 3) Unplug electronics when not in use, 4) Improve home insulation. These actions can reduce your energy consumption by 20-30%.",
                        "transport": "For sustainable transportation: 1) Walk or bike for short trips, 2) Use public transportation, 3) Consider electric or hybrid vehicles, 4) Carpool when possible. Transportation accounts for about 29% of greenhouse gas emissions.",
                        "carbon": "To reduce your carbon footprint: 1) Eat less meat, 2) Buy local and seasonal food, 3) Reduce air travel, 4) Use renewable energy, 5) Practice the 3 R's: Reduce, Reuse, Recycle.",
                        "default": "I'm here to help with climate action advice! In demo mode, I can provide general guidance on energy efficiency, sustainable transportation, carbon footprint reduction, and environmental best practices. What specific area would you like to explore?"
                    }
                    
                    # Simple keyword matching for demo
                    response = demo_responses["default"]
                    prompt_lower = prompt.lower()
                    if any(word in prompt_lower for word in ["energy", "electricity", "power", "heating", "cooling"]):
                        response = demo_responses["energy"]
                    elif any(word in prompt_lower for word in ["transport", "car", "travel", "commute", "bike", "walk"]):
                        response = demo_responses["transport"]
                    elif any(word in prompt_lower for word in ["carbon", "footprint", "emissions", "reduce", "impact"]):
                        response = demo_responses["carbon"]
                    
                    st.markdown(response)
                    st.info("💡 This is a demo response. Full AI capabilities require proper API configuration.")
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    try:
                        response, sources = rag_system.retrieve_and_generate(prompt, user_profile)
                        st.markdown(response)
                        
                        # Show sources if available
                        if sources:
                            with st.expander("📚 Sources"):
                                for source in sources[:2]:
                                    st.write(f"• {source['metadata'].get('title', 'Climate Data')} (Relevance: {source['similarity']:.1%})")
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = f"I apologize, but I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💡 Energy saving tips"):
            st.session_state.messages.append({"role": "user", "content": "What are the best energy saving tips for my home?"})
            st.rerun()
    
    with col2:
        if st.button("🚗 Transportation options"):
            st.session_state.messages.append({"role": "user", "content": "What are sustainable transportation options in my area?"})
            st.rerun()
    
    with col3:
        if st.button("🌱 Carbon footprint"):
            st.session_state.messages.append({"role": "user", "content": "How can I reduce my carbon footprint?"})
            st.rerun()

def display_community(impact_tracker, demo_mode=False):
    """Display community features and leaderboard"""
    st.header("🏆 Community Impact")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🥇 Impact Leaderboard")
        
        metric_choice = st.selectbox("Rank by:", ["carbon_saved_kg", "total_actions", "energy_saved_kwh"])
        
        leaderboard = impact_tracker.get_leaderboard(metric=metric_choice, limit=10)
        
        if leaderboard:
            # Create leaderboard dataframe
            df = pd.DataFrame(leaderboard)
            
            # Display as table
            st.dataframe(
                df[['user_id', metric_choice, 'total_actions']].rename(columns={
                    'user_id': 'User',
                    'carbon_saved_kg': 'Carbon Saved (kg)',
                    'total_actions': 'Total Actions',
                    'energy_saved_kwh': 'Energy Saved (kWh)'
                }),
                use_container_width=True
            )
            
            # Create visualization
            if len(df) > 0:
                fig = px.bar(
                    df.head(5), 
                    x='user_id', 
                    y=metric_choice,
                    title=f"Top 5 Users by {metric_choice.replace('_', ' ').title()}",
                    color=metric_choice,
                    color_continuous_scale="Greens"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No community data available yet. Start logging your climate actions to appear on the leaderboard!")
    
    with col2:
        st.subheader("🌍 Global Impact")
        
        # Mock global statistics
        st.metric("🌱 Total CO2 Saved", "12,450 kg", "↗️ +15% this month")
        st.metric("👥 Active Users", "1,247", "↗️ +8% this month")
        st.metric("📊 Actions Logged", "5,632", "↗️ +22% this month")
        
        st.markdown("### 🎯 Monthly Challenge")
        st.info("**December Challenge:** Reduce energy consumption by 20%")
        
        progress = 65  # Mock progress
        st.progress(progress / 100)
        st.write(f"Community Progress: {progress}%")

def get_action_subtypes(action_type):
    """Get subtypes for action categories"""
    subtypes = {
        "energy_efficiency": ["led_bulb_replacement", "insulation_improvement", "smart_thermostat", "energy_efficient_appliance"],
        "transportation": ["bike_commute_km", "public_transport_km", "electric_vehicle", "carpooling", "walking"],
        "renewable_energy": ["solar_panel_kw", "wind_turbine_kw", "green_energy_plan"],
        "food": ["vegetarian_meal", "local_food_kg", "food_waste_reduction_kg", "composting_kg"],
        "water": ["low_flow_fixture", "rainwater_harvesting", "drought_resistant_landscaping"],
        "waste": ["recycling_kg", "reusable_bag", "composting_kg", "electronic_recycling_kg"]
    }
    return subtypes.get(action_type, ["general"])

def get_action_examples(action_type):
    """Get example actions for categories"""
    examples = {
        "energy_efficiency": ["Replace 5 incandescent bulbs with LEDs", "Install programmable thermostat", "Add insulation to attic"],
        "transportation": ["Bike to work (10 km)", "Take public transit instead of driving", "Carpool with colleagues"],
        "renewable_energy": ["Install 5kW solar panel system", "Switch to renewable energy plan"],
        "food": ["Eat vegetarian meal instead of meat", "Buy local produce", "Compost food scraps"],
        "water": ["Install low-flow showerhead", "Set up rain barrel", "Plant drought-resistant garden"],
        "waste": ["Recycle electronics", "Use reusable shopping bags", "Compost organic waste"]
    }
    return examples.get(action_type, ["Log any climate-positive action"])

if __name__ == "__main__":
    main()