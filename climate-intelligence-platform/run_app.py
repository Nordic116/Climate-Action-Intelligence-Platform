#!/usr/bin/env python3
"""
Climate Intelligence Platform - Main Application Runner

This script provides multiple ways to run the application:
1. Streamlit web interface
2. FastAPI backend server
3. Interactive CLI demo
4. Jupyter notebook server
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_streamlit():
    """Run the Streamlit web interface"""
    logger.info("Starting Streamlit web interface...")
    
    streamlit_app = os.path.join(os.path.dirname(__file__), "frontend", "streamlit_app.py")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", streamlit_app,
        "--server.port", str(settings.port),
        "--server.address", settings.host,
        "--server.allowRunOnSave", "true",
        "--server.runOnSave", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Streamlit: {e}")
        print("Error: Streamlit failed to start. Make sure it's installed:")
        print("pip install streamlit")
    except KeyboardInterrupt:
        logger.info("Streamlit server stopped by user")


def run_fastapi():
    """Run the FastAPI backend server"""
    logger.info("Starting FastAPI backend server...")
    
    try:
        import uvicorn
        from src.api.main import app
        
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port + 1,  # Use different port for API
            reload=settings.reload,
            log_level=settings.log_level.lower()
        )
    except ImportError:
        logger.error("FastAPI/uvicorn not available")
        print("Error: FastAPI or uvicorn not installed. Install with:")
        print("pip install fastapi uvicorn")
    except KeyboardInterrupt:
        logger.info("FastAPI server stopped by user")


def run_cli_demo():
    """Run interactive CLI demo"""
    logger.info("Starting CLI demo...")
    
    try:
        from src.core.rag_system import RAGSystem
        from src.services.climate_data_service import ClimateDataService
        import asyncio
        
        async def cli_demo():
            print("🌍 Climate Intelligence Platform - CLI Demo")
            print("=" * 50)
            
            # Initialize systems
            print("Initializing systems...")
            rag_system = RAGSystem()
            climate_service = ClimateDataService()
            
            # Load README
            readme_path = os.path.join(os.path.dirname(__file__), "README.md")
            if os.path.exists(readme_path):
                stats = rag_system.add_documents([readme_path])
                print(f"✅ Loaded README: {stats.get('total_chunks', 0)} chunks")
            else:
                print("⚠️  README.md not found")
            
            print("\nAvailable commands:")
            print("1. 'ask <question>' - Ask a question about climate intelligence")
            print("2. 'weather <location>' - Get weather data for a location")
            print("3. 'carbon <activity> <amount>' - Calculate carbon footprint")
            print("4. 'info' - Show system information")
            print("5. 'quit' - Exit the demo")
            print()
            
            while True:
                try:
                    user_input = input("🌍 > ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    parts = user_input.split()
                    command = parts[0].lower()
                    
                    if command == 'ask' and len(parts) > 1:
                        question = ' '.join(parts[1:])
                        print(f"🤔 Thinking about: {question}")
                        
                        response = await rag_system.query(question)
                        print(f"🤖 Answer: {response['answer']}")
                        
                        if response.get('sources'):
                            print(f"📚 Sources: {len(response['sources'])} documents")
                    
                    elif command == 'weather' and len(parts) > 1:
                        location = ' '.join(parts[1:])
                        print(f"🌤️  Getting weather for: {location}")
                        
                        async with climate_service:
                            weather_data = await climate_service.get_weather_data(location)
                            current = weather_data.get('current', {})
                            print(f"🌡️  Temperature: {current.get('temperature', 'N/A')}°C")
                            print(f"💧 Humidity: {current.get('humidity', 'N/A')}%")
                            print(f"📝 Conditions: {current.get('description', 'N/A')}")
                    
                    elif command == 'carbon' and len(parts) >= 3:
                        activity = parts[1]
                        try:
                            amount = float(parts[2])
                            print(f"🌱 Calculating carbon footprint for {amount} {activity}")
                            
                            async with climate_service:
                                carbon_data = await climate_service.get_carbon_data(activity, amount=amount)
                                print(f"💨 CO₂ Emissions: {carbon_data.get('carbon_footprint_kg', 0):.2f} kg")
                                print(f"🌳 Trees to offset: {carbon_data.get('equivalent_trees', 0):.1f}")
                        except ValueError:
                            print("❌ Invalid amount. Please enter a number.")
                    
                    elif command == 'info':
                        system_info = rag_system.get_system_info()
                        print("ℹ️  System Information:")
                        print(f"   LLM Provider: {system_info.get('llm_provider', 'Unknown')}")
                        print(f"   Vector DB: {system_info.get('vector_db_type', 'Unknown')}")
                        collection_info = system_info.get('collection_info', {})
                        print(f"   Documents: {collection_info.get('count', 0)}")
                    
                    else:
                        print("❌ Unknown command. Type 'quit' to exit.")
                    
                    print()
                
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        asyncio.run(cli_demo())
        
    except ImportError as e:
        logger.error(f"CLI demo dependencies not available: {e}")
        print("Error: Required dependencies not installed")
    except KeyboardInterrupt:
        logger.info("CLI demo stopped by user")


def run_jupyter():
    """Run Jupyter notebook server"""
    logger.info("Starting Jupyter notebook server...")
    
    notebook_dir = os.path.join(os.path.dirname(__file__), "docs", "notebooks")
    os.makedirs(notebook_dir, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "jupyter", "notebook",
        "--notebook-dir", notebook_dir,
        "--ip", settings.host,
        "--port", str(settings.port + 2),
        "--no-browser",
        "--allow-root"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Jupyter: {e}")
        print("Error: Jupyter not installed. Install with:")
        print("pip install jupyter")
    except KeyboardInterrupt:
        logger.info("Jupyter server stopped by user")


def install_dependencies():
    """Install required dependencies"""
    logger.info("Installing dependencies...")
    
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if os.path.exists(requirements_file):
        cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
        try:
            subprocess.run(cmd, check=True)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            print("❌ Failed to install dependencies")
    else:
        print("❌ requirements.txt not found")


def check_environment():
    """Check if environment is properly configured"""
    logger.info("Checking environment...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check for .env file (optional)
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("ℹ️  .env file not found (optional - using defaults)")
    
    # Check critical dependencies
    critical_deps = ['streamlit', 'fastapi', 'langchain', 'chromadb']
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            issues.append(f"Missing dependency: {dep}")
    
    if issues:
        print("⚠️  Environment Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nRun 'python run_app.py --install' to install dependencies")
    else:
        print("✅ Environment looks good!")
    
    return len(issues) == 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Climate Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_app.py                    # Run Streamlit web interface
  python run_app.py --mode api         # Run FastAPI backend
  python run_app.py --mode cli         # Run CLI demo
  python run_app.py --mode jupyter     # Run Jupyter notebooks
  python run_app.py --install          # Install dependencies
  python run_app.py --check            # Check environment
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["streamlit", "api", "cli", "jupyter"],
        default="streamlit",
        help="Application mode to run (default: streamlit)"
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install required dependencies"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check environment configuration"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to run on (default: {settings.port})"
    )
    
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})"
    )
    
    args = parser.parse_args()
    
    # Update settings with command line args
    settings.port = args.port
    settings.host = args.host
    
    if args.install:
        install_dependencies()
        return
    
    if args.check:
        check_environment()
        return
    
    # Check environment before running
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues before running.")
        return
    
    print(f"🚀 Starting Climate Intelligence Platform in {args.mode} mode...")
    print(f"📍 Host: {settings.host}:{settings.port}")
    print(f"🔧 Debug: {settings.debug}")
    print()
    
    try:
        if args.mode == "streamlit":
            run_streamlit()
        elif args.mode == "api":
            run_fastapi()
        elif args.mode == "cli":
            run_cli_demo()
        elif args.mode == "jupyter":
            run_jupyter()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()