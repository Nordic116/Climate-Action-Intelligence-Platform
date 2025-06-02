"""Streamlit frontend for Climate Intelligence Platform"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
except ImportError as e:
    st = None
    px = None
    go = None
    pd = None
    np = None
    print(f"Import error: {e}")

from src.core.rag_system import RAGSystem
from src.services.climate_data_service import ClimateDataService
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClimateIntelligenceApp:
    """Main Streamlit application class"""
    
    def __init__(self):
        self.rag_system = None
        self.climate_service = None
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'rag_initialized' not in st.session_state:
            st.session_state.rag_initialized = False
        
        if 'climate_data_cache' not in st.session_state:
            st.session_state.climate_data_cache = {}
    
    def initialize_systems(self):
        """Initialize RAG and climate systems"""
        if not st.session_state.rag_initialized:
            with st.spinner("Initializing Climate Intelligence Platform..."):
                try:
                    self.rag_system = RAGSystem()
                    self.climate_service = ClimateDataService()
                    
                    # Load README if available
                    readme_path = os.path.join(os.path.dirname(__file__), "../../README.md")
                    if os.path.exists(readme_path):
                        stats = self.rag_system.add_documents([readme_path])
                        st.success(f"Loaded README: {stats.get('total_chunks', 0)} chunks")
                    
                    st.session_state.rag_initialized = True
                    
                except Exception as e:
                    st.error(f"Error initializing systems: {e}")
                    logger.error(f"Initialization error: {e}")
    
    def run(self):
        """Main application runner"""
        if not st:
            print("Streamlit not available")
            return
        
        st.set_page_config(
            page_title="Climate Intelligence Platform",
            page_icon="🌍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #2E8B57;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f8f0;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #2E8B57;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .assistant-message {
            background-color: #f1f8e9;
            border-left: 4px solid #4caf50;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">🌍 Climate Intelligence Platform</h1>', unsafe_allow_html=True)
        st.markdown("*Advanced RAG application for climate action intelligence*")
        
        # Initialize systems
        self.initialize_systems()
        
        # Sidebar
        self.render_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🌡️ Climate Data", "📊 Analytics", "⚙️ System"])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_climate_data_interface()
        
        with tab3:
            self.render_analytics_interface()
        
        with tab4:
            self.render_system_interface()
    
    def render_sidebar(self):
        """Render sidebar with controls"""
        st.sidebar.header("🔧 Controls")
        
        # File upload
        st.sidebar.subheader("📄 Document Upload")
        uploaded_file = st.sidebar.file_uploader(
            "Upload documents",
            type=['txt', 'md', 'pdf', 'docx', 'csv'],
            help="Upload documents to add to the knowledge base"
        )
        
        if uploaded_file and self.rag_system:
            if st.sidebar.button("Process Document"):
                with st.spinner("Processing document..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Process the document
                        stats = self.rag_system.add_documents([temp_path])
                        st.sidebar.success(f"Processed: {stats.get('total_chunks', 0)} chunks")
                        
                        # Clean up
                        os.remove(temp_path)
                        
                    except Exception as e:
                        st.sidebar.error(f"Error processing document: {e}")
        
        # Text input
        st.sidebar.subheader("📝 Add Text")
        text_input = st.sidebar.text_area("Enter text to add to knowledge base")
        if st.sidebar.button("Add Text") and text_input and self.rag_system:
            try:
                stats = self.rag_system.add_text(text_input, "user_input")
                st.sidebar.success(f"Added: {stats.get('total_chunks', 0)} chunks")
            except Exception as e:
                st.sidebar.error(f"Error adding text: {e}")
        
        # Settings
        st.sidebar.subheader("⚙️ Settings")
        st.sidebar.slider("Response Temperature", 0.0, 1.0, 0.7, key="temperature")
        st.sidebar.slider("Number of Sources", 1, 10, 5, key="num_sources")
        st.sidebar.checkbox("Include Sources", True, key="include_sources")
        
        # System info
        if self.rag_system:
            st.sidebar.subheader("📊 System Status")
            try:
                system_info = self.rag_system.get_system_info()
                st.sidebar.metric("LLM Provider", system_info.get('llm_provider', 'Unknown'))
                
                collection_info = system_info.get('collection_info', {})
                if collection_info:
                    st.sidebar.metric("Documents", collection_info.get('count', 0))
            except Exception as e:
                st.sidebar.error(f"Error getting system info: {e}")
    
    def render_chat_interface(self):
        """Render chat interface"""
        st.header("💬 Climate Intelligence Chat")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(message["sources"]):
                            st.write(f"**Source {i+1}:** {source.get('source', 'Unknown')}")
                            if source.get('section'):
                                st.write(f"*Section:* {source['section']}")
                            st.write(f"*Relevance:* {source.get('relevance_score', 0):.2f}")
                            st.divider()
        
        # Chat input
        if prompt := st.chat_input("Ask about climate action and environmental intelligence..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            if self.rag_system:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = asyncio.run(self.rag_system.query(
                                question=prompt,
                                k=st.session_state.num_sources,
                                include_sources=st.session_state.include_sources,
                                temperature=st.session_state.temperature
                            ))
                            
                            st.markdown(response["answer"])
                            
                            # Add assistant message
                            message_data = {
                                "role": "assistant",
                                "content": response["answer"]
                            }
                            
                            if response.get("sources"):
                                message_data["sources"] = response["sources"]
                                
                                # Display sources
                                with st.expander("📚 Sources"):
                                    for i, source in enumerate(response["sources"]):
                                        st.write(f"**Source {i+1}:** {source.get('source', 'Unknown')}")
                                        if source.get('section'):
                                            st.write(f"*Section:* {source['section']}")
                                        st.write(f"*Relevance:* {source.get('relevance_score', 0):.2f}")
                                        st.divider()
                            
                            st.session_state.messages.append(message_data)
                            
                        except Exception as e:
                            error_msg = f"Error generating response: {e}"
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })
            else:
                st.error("RAG system not initialized")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    def render_climate_data_interface(self):
        """Render climate data interface"""
        st.header("🌡️ Climate Data Dashboard")
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            location = st.text_input("Location", value="London", key="climate_location")
            data_type = st.selectbox(
                "Data Type",
                ["comprehensive", "weather", "air_quality", "trends"],
                key="climate_data_type"
            )
            
            if st.button("🔄 Fetch Climate Data"):
                if self.climate_service:
                    with st.spinner("Fetching climate data..."):
                        try:
                            data = asyncio.run(self._fetch_climate_data(location, data_type))
                            st.session_state.climate_data_cache[f"{location}_{data_type}"] = data
                        except Exception as e:
                            st.error(f"Error fetching climate data: {e}")
        
        with col1:
            # Display cached data
            cache_key = f"{st.session_state.climate_location}_{st.session_state.climate_data_type}"
            if cache_key in st.session_state.climate_data_cache:
                data = st.session_state.climate_data_cache[cache_key]
                self._display_climate_data(data)
            else:
                st.info("Click 'Fetch Climate Data' to load information")
    
    async def _fetch_climate_data(self, location: str, data_type: str):
        """Fetch climate data asynchronously"""
        async with self.climate_service:
            if data_type == "weather":
                return await self.climate_service.get_weather_data(location)
            elif data_type == "air_quality":
                return await self.climate_service.get_air_quality_data(location)
            elif data_type == "trends":
                return await self.climate_service.get_climate_trends(location)
            else:  # comprehensive
                return await self.climate_service.get_comprehensive_climate_report(location)
    
    def _display_climate_data(self, data: Dict[str, Any]):
        """Display climate data with visualizations"""
        if not data:
            return
        
        st.subheader(f"📍 {data.get('location', 'Unknown Location')}")
        
        # Weather data
        if 'weather' in data or 'current' in data:
            weather_data = data.get('weather', data)
            current = weather_data.get('current', {})
            
            if current:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🌡️ Temperature", f"{current.get('temperature', 'N/A')}°C")
                
                with col2:
                    st.metric("💧 Humidity", f"{current.get('humidity', 'N/A')}%")
                
                with col3:
                    st.metric("🌪️ Wind Speed", f"{current.get('wind_speed', 'N/A')} m/s")
                
                with col4:
                    st.metric("📊 Pressure", f"{current.get('pressure', 'N/A')} hPa")
                
                st.write(f"**Conditions:** {current.get('description', 'N/A')}")
            
            # Forecast
            forecast = weather_data.get('forecast', [])
            if forecast and px:
                df_forecast = pd.DataFrame(forecast)
                if 'max_temp' in df_forecast.columns:
                    fig = px.line(
                        df_forecast,
                        x='date',
                        y=['max_temp', 'min_temp'],
                        title="Temperature Forecast",
                        labels={'value': 'Temperature (°C)', 'date': 'Date'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Air quality data
        if 'air_quality' in data:
            air_quality = data['air_quality']
            st.subheader("🌬️ Air Quality")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("AQI", air_quality.get('aqi', 'N/A'))
            with col2:
                st.metric("Category", air_quality.get('category', 'N/A'))
            
            pollutants = air_quality.get('pollutants', {})
            if pollutants and px:
                df_pollutants = pd.DataFrame([pollutants]).T.reset_index()
                df_pollutants.columns = ['Pollutant', 'Concentration']
                
                fig = px.bar(
                    df_pollutants,
                    x='Pollutant',
                    y='Concentration',
                    title="Pollutant Concentrations"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Climate trends
        if 'climate_trends' in data:
            trends = data['climate_trends']
            st.subheader("📈 Climate Trends")
            
            temp_trends = trends.get('temperature_trends', [])
            if temp_trends and px:
                df_trends = pd.DataFrame(temp_trends)
                
                fig = px.line(
                    df_trends,
                    x='year',
                    y='avg_temperature',
                    title="Average Temperature Trends",
                    labels={'avg_temperature': 'Temperature (°C)', 'year': 'Year'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Summary
        if 'summary' in data:
            st.subheader("📋 Summary")
            summary = data['summary']
            for key, value in summary.items():
                if isinstance(value, list):
                    st.write(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        st.write(f"• {item}")
                else:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    def render_analytics_interface(self):
        """Render analytics interface"""
        st.header("📊 Climate Analytics")
        
        # Carbon footprint calculator
        st.subheader("🌱 Carbon Footprint Calculator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            activity_type = st.selectbox(
                "Activity Type",
                ["electricity", "gas", "car", "flight", "train"],
                key="carbon_activity"
            )
        
        with col2:
            amount = st.number_input("Amount", min_value=0.0, value=100.0, key="carbon_amount")
        
        with col3:
            if st.button("Calculate Carbon Footprint"):
                if self.climate_service:
                    try:
                        data = asyncio.run(self.climate_service.get_carbon_data(
                            activity_type=activity_type,
                            amount=amount
                        ))
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("CO₂ Emissions", f"{data.get('carbon_footprint_kg', 0):.2f} kg")
                        with col_b:
                            st.metric("Trees to Offset", f"{data.get('equivalent_trees', 0):.1f}")
                        with col_c:
                            st.metric("Activity", f"{amount} {activity_type}")
                        
                        recommendations = data.get('recommendations', [])
                        if recommendations:
                            st.write("**Recommendations:**")
                            for rec in recommendations:
                                st.write(f"• {rec}")
                    
                    except Exception as e:
                        st.error(f"Error calculating carbon footprint: {e}")
        
        # Sample analytics charts
        if px and np:
            st.subheader("📈 Sample Climate Analytics")
            
            # Generate sample data
            dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='M')
            temp_data = 15 + 5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 12) + np.random.normal(0, 1, len(dates))
            
            df_sample = pd.DataFrame({
                'Date': dates,
                'Temperature': temp_data,
                'CO2_Levels': 400 + np.cumsum(np.random.normal(0.1, 0.5, len(dates)))
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.line(
                    df_sample,
                    x='Date',
                    y='Temperature',
                    title="Temperature Trends (Sample Data)"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.line(
                    df_sample,
                    x='Date',
                    y='CO2_Levels',
                    title="CO₂ Levels (Sample Data)"
                )
                st.plotly_chart(fig2, use_container_width=True)
    
    def render_system_interface(self):
        """Render system interface"""
        st.header("⚙️ System Information")
        
        if self.rag_system:
            try:
                system_info = self.rag_system.get_system_info()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🤖 LLM Configuration")
                    st.write(f"**Current Provider:** {system_info.get('llm_provider', 'Unknown')}")
                    st.write(f"**Available Providers:** {', '.join(system_info.get('available_providers', []))}")
                    st.write(f"**Embedding Model:** {system_info.get('embedding_model', 'Unknown')}")
                
                with col2:
                    st.subheader("🗄️ Vector Database")
                    collection_info = system_info.get('collection_info', {})
                    st.write(f"**Type:** {system_info.get('vector_db_type', 'Unknown')}")
                    st.write(f"**Collection:** {collection_info.get('name', 'Unknown')}")
                    st.write(f"**Document Count:** {collection_info.get('count', 0)}")
                
                # Environment info
                st.subheader("🌐 Environment")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("App Version", settings.app_version)
                with col2:
                    st.metric("Debug Mode", settings.debug)
                with col3:
                    st.metric("Log Level", settings.log_level)
                
                # Feature flags
                st.subheader("🚩 Feature Flags")
                features = {
                    "Real-time Data": settings.enable_real_time_data,
                    "Advanced Analytics": settings.enable_advanced_analytics,
                    "External APIs": settings.enable_external_apis,
                    "Caching": settings.enable_caching,
                    "Monitoring": settings.enable_monitoring
                }
                
                for feature, enabled in features.items():
                    st.write(f"**{feature}:** {'✅ Enabled' if enabled else '❌ Disabled'}")
                
                # Database management
                st.subheader("🗃️ Database Management")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🗑️ Clear Database", type="secondary"):
                        if st.session_state.get('confirm_clear', False):
                            self.rag_system.clear_database()
                            st.success("Database cleared successfully!")
                            st.session_state.confirm_clear = False
                        else:
                            st.session_state.confirm_clear = True
                            st.warning("Click again to confirm database clearing")
                
                with col2:
                    if st.button("🔄 Reload README"):
                        readme_path = os.path.join(os.path.dirname(__file__), "../../README.md")
                        if os.path.exists(readme_path):
                            stats = self.rag_system.add_documents([readme_path])
                            st.success(f"README reloaded: {stats.get('total_chunks', 0)} chunks")
                        else:
                            st.error("README.md not found")
                
            except Exception as e:
                st.error(f"Error getting system information: {e}")
        else:
            st.error("RAG system not initialized")


def main():
    """Main function to run the Streamlit app"""
    app = ClimateIntelligenceApp()
    app.run()


if __name__ == "__main__":
    main()