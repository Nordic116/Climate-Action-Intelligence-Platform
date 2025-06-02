# 🌍 Climate Intelligence Platform

An advanced Retrieval-Augmented Generation (RAG) application for climate action intelligence, built with modern AI technologies and comprehensive environmental data integration.

## 🚀 Features

### Core RAG Capabilities
- **Multi-Provider LLM Support**: OpenAI, Anthropic, Azure OpenAI, Hugging Face
- **Advanced Document Processing**: PDF, DOCX, Markdown, CSV, Excel support
- **Vector Database**: ChromaDB with persistent storage
- **Intelligent Chunking**: Context-aware document segmentation
- **Source Attribution**: Detailed source tracking and relevance scoring

### Climate Data Integration
- **Real-time Weather Data**: OpenWeatherMap, WeatherAPI integration
- **Air Quality Monitoring**: Comprehensive pollutant tracking
- **Climate Trends Analysis**: Historical climate data processing
- **Carbon Footprint Calculator**: Activity-based emissions calculation
- **Renewable Energy Assessment**: Solar and wind potential analysis

### User Interfaces
- **Streamlit Web App**: Interactive chat interface with visualizations
- **FastAPI Backend**: RESTful API for external integrations
- **CLI Demo**: Command-line interface for quick testing
- **Jupyter Notebooks**: Data science and analysis environment

### Advanced Features
- **Async Processing**: High-performance async operations
- **Caching System**: Redis-based caching for improved performance
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Docker Support**: Containerized deployment with docker-compose
- **Comprehensive Logging**: Structured logging with multiple levels

## 🛠️ Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nordic116/Climate-Action-Intelligence-Platform.git
   cd Climate-Action-Intelligence-Platform/climate-intelligence-platform
   ```

2. **Install dependencies**:
   ```bash
   python run_app.py --install
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**:
   ```bash
   python run_app.py
   ```

### Docker Deployment

1. **Using Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Access the application**:
   - Streamlit Web App: http://localhost:12000
   - FastAPI Backend: http://localhost:12001
   - Grafana Dashboard: http://localhost:3000
   - Jupyter Notebooks: http://localhost:8888

## 🔧 Configuration

### Environment Variables

The application supports extensive configuration through environment variables. Copy `.env.example` to `.env` and configure:

#### AI/LLM APIs
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
HUGGINGFACE_API_TOKEN=hf_your-huggingface-token-here
```

#### Climate Data APIs
```bash
OPENWEATHER_API_KEY=your-openweather-api-key
WEATHERAPI_KEY=your-weatherapi-key
NASA_API_KEY=your-nasa-api-key
```

#### Database Configuration
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/climate_db
REDIS_URL=redis://localhost:6379/0
```

### Feature Flags
```bash
ENABLE_REAL_TIME_DATA=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_EXTERNAL_APIS=true
ENABLE_CACHING=true
ENABLE_MONITORING=true
```

## 📖 Usage

### Web Interface (Streamlit)

1. **Start the web application**:
   ```bash
   python run_app.py --mode streamlit
   ```

2. **Access features**:
   - **Chat Tab**: Ask questions about climate intelligence
   - **Climate Data Tab**: Get real-time weather and environmental data
   - **Analytics Tab**: Calculate carbon footprints and view trends
   - **System Tab**: Monitor system status and manage database

### API Backend (FastAPI)

1. **Start the API server**:
   ```bash
   python run_app.py --mode api
   ```

2. **API Endpoints**:
   - `POST /query`: Query the RAG system
   - `POST /upload`: Upload documents
   - `GET /climate-data`: Get climate data
   - `GET /carbon-footprint`: Calculate emissions
   - `GET /system-info`: System information

3. **API Documentation**: http://localhost:12001/docs

### CLI Demo

```bash
python run_app.py --mode cli
```

**Available commands**:
- `ask <question>`: Ask about climate intelligence
- `weather <location>`: Get weather data
- `carbon <activity> <amount>`: Calculate carbon footprint
- `info`: Show system information
- `quit`: Exit

### Jupyter Notebooks

```bash
python run_app.py --mode jupyter
```

Access notebooks at http://localhost:8888 for data analysis and experimentation.

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • Streamlit     │◄──►│ • FastAPI       │◄──►│ • ChromaDB      │
│ • Jupyter       │    │ • RAG System    │    │ • PostgreSQL    │
│ • CLI           │    │ • LLM Manager   │    │ • Redis Cache   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ External APIs   │
                    │                 │
                    │ • OpenAI        │
                    │ • Anthropic     │
                    │ • Weather APIs  │
                    │ • Climate Data  │
                    └─────────────────┘
```

### Core Classes

- **RAGSystem**: Main orchestrator for retrieval-augmented generation
- **LLMManager**: Multi-provider LLM abstraction layer
- **DocumentProcessor**: Advanced document parsing and chunking
- **ClimateDataService**: External climate data integration
- **VectorDatabase**: Vector storage abstraction (ChromaDB implementation)

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest --cov=src tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/ -v
```

## 📊 Monitoring

### Metrics Collection
- **Prometheus**: Application metrics
- **Grafana**: Visualization dashboards
- **Structured Logging**: JSON-formatted logs

### Health Checks
- Application health: `/health`
- Database connectivity
- External API status
- System resource usage

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**:
   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   export LOG_LEVEL=WARNING
   ```

2. **Docker Production**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Kubernetes** (optional):
   ```bash
   kubectl apply -f k8s/
   ```

### Scaling Considerations

- **Horizontal Scaling**: Multiple application instances
- **Database Scaling**: Read replicas for PostgreSQL
- **Cache Optimization**: Redis clustering
- **Load Balancing**: Nginx or cloud load balancers

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/
flake8 src/
```

## 📝 API Documentation

### Query Endpoint

```bash
curl -X POST "http://localhost:12001/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is ClimateIQ?",
       "k": 5,
       "include_sources": true,
       "temperature": 0.7
     }'
```

### Climate Data Endpoint

```bash
curl "http://localhost:12001/climate-data?location=London&data_type=comprehensive"
```

### Upload Document

```bash
curl -X POST "http://localhost:12001/upload" \
     -F "file=@document.pdf"
```

## 🔒 Security

- **API Key Management**: Environment-based configuration
- **Input Validation**: Pydantic models for request validation
- **Rate Limiting**: Configurable request limits
- **CORS Configuration**: Secure cross-origin requests
- **Health Checks**: Automated system monitoring

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For RAG framework and LLM integrations
- **ChromaDB**: For vector database capabilities
- **Streamlit**: For rapid web interface development
- **FastAPI**: For high-performance API backend
- **Climate Data Providers**: OpenWeatherMap, WeatherAPI, NASA, NOAA

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Nordic116/Climate-Action-Intelligence-Platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Nordic116/Climate-Action-Intelligence-Platform/discussions)
- **Documentation**: [Wiki](https://github.com/Nordic116/Climate-Action-Intelligence-Platform/wiki)

---

**Built with ❤️ for climate action and environmental intelligence**