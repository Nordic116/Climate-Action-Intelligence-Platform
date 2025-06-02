"""FastAPI main application"""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    HTTPException = None
    UploadFile = None
    File = None
    Depends = None
    BackgroundTasks = None
    CORSMiddleware = None
    JSONResponse = None
    BaseModel = None

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rag_system import RAGSystem
from services.climate_data_service import ClimateDataService
from config.settings import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Global instances
rag_system = None
climate_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_system, climate_service
    
    # Startup
    logger.info("Starting Climate Intelligence Platform API")
    
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Initialize climate service
    climate_service = ClimateDataService()
    
    # Load README if available
    readme_path = os.path.join(os.path.dirname(__file__), "../../../README.md")
    if os.path.exists(readme_path):
        try:
            stats = rag_system.add_documents([readme_path])
            logger.info(f"Loaded README: {stats}")
        except Exception as e:
            logger.error(f"Error loading README: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Climate Intelligence Platform API")


# Create FastAPI app
if FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Advanced RAG application for climate action intelligence",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None
    logger.error("FastAPI not available")


# Pydantic models
if BaseModel:
    class QueryRequest(BaseModel):
        question: str
        k: int = 5
        include_sources: bool = True
        temperature: float = 0.7
    
    class QueryResponse(BaseModel):
        answer: str
        sources: List[Dict[str, Any]] = []
        retrieved_docs: int = 0
        query: str
    
    class DocumentUploadResponse(BaseModel):
        message: str
        stats: Dict[str, Any]
    
    class ClimateDataRequest(BaseModel):
        location: str
        data_type: str = "comprehensive"  # weather, air_quality, trends, comprehensive
    
    class SystemInfoResponse(BaseModel):
        system_info: Dict[str, Any]
        collection_info: Dict[str, Any]
        available_endpoints: List[str]


# API Routes
if app:
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Climate Intelligence Platform API",
            "version": settings.app_version,
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": "2024-06-02T00:00:00Z",
            "services": {
                "rag_system": rag_system is not None,
                "climate_service": climate_service is not None
            }
        }
    
    @app.post("/query", response_model=QueryResponse if BaseModel else dict)
    async def query_rag(request: QueryRequest if BaseModel else dict):
        """Query the RAG system"""
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        try:
            if BaseModel:
                result = await rag_system.query(
                    question=request.question,
                    k=request.k,
                    include_sources=request.include_sources,
                    temperature=request.temperature
                )
            else:
                # Fallback for when Pydantic is not available
                result = await rag_system.query(
                    question=request.get("question", ""),
                    k=request.get("k", 5),
                    include_sources=request.get("include_sources", True),
                    temperature=request.get("temperature", 0.7)
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/upload", response_model=DocumentUploadResponse if BaseModel else dict)
    async def upload_document(file: UploadFile = File(...)):
        """Upload and process a document"""
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        try:
            # Save uploaded file temporarily
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Process the document
            stats = rag_system.add_documents([temp_path])
            
            # Clean up
            os.remove(temp_path)
            
            return {
                "message": f"Document {file.filename} processed successfully",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/add-text")
    async def add_text(text: str, source: str = "api_input"):
        """Add raw text to the RAG system"""
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        try:
            stats = rag_system.add_text(text, source)
            return {
                "message": "Text added successfully",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error adding text: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/climate-data")
    async def get_climate_data(location: str, data_type: str = "comprehensive"):
        """Get climate data for a location"""
        if not climate_service:
            raise HTTPException(status_code=503, detail="Climate service not available")
        
        try:
            async with climate_service:
                if data_type == "weather":
                    data = await climate_service.get_weather_data(location)
                elif data_type == "air_quality":
                    data = await climate_service.get_air_quality_data(location)
                elif data_type == "trends":
                    data = await climate_service.get_climate_trends(location)
                elif data_type == "comprehensive":
                    data = await climate_service.get_comprehensive_climate_report(location)
                else:
                    raise HTTPException(status_code=400, detail="Invalid data_type")
                
                return data
                
        except Exception as e:
            logger.error(f"Error fetching climate data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/carbon-footprint")
    async def calculate_carbon_footprint(
        activity_type: str,
        amount: float,
        unit: str = "default"
    ):
        """Calculate carbon footprint for an activity"""
        if not climate_service:
            raise HTTPException(status_code=503, detail="Climate service not available")
        
        try:
            async with climate_service:
                data = await climate_service.get_carbon_data(
                    activity_type=activity_type,
                    amount=amount,
                    unit=unit
                )
                return data
                
        except Exception as e:
            logger.error(f"Error calculating carbon footprint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/system-info", response_model=SystemInfoResponse if BaseModel else dict)
    async def get_system_info():
        """Get system information"""
        try:
            system_info = {}
            collection_info = {}
            
            if rag_system:
                system_info = rag_system.get_system_info()
                if hasattr(rag_system.vector_db, 'get_collection_info'):
                    collection_info = rag_system.vector_db.get_collection_info()
            
            available_endpoints = [
                "/",
                "/health",
                "/query",
                "/upload",
                "/add-text",
                "/climate-data",
                "/carbon-footprint",
                "/system-info",
                "/batch-query",
                "/clear-database"
            ]
            
            return {
                "system_info": system_info,
                "collection_info": collection_info,
                "available_endpoints": available_endpoints
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/batch-query")
    async def batch_query(questions: List[str], k: int = 5, include_sources: bool = False):
        """Process multiple queries in batch"""
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        try:
            results = await rag_system.batch_query(
                questions=questions,
                k=k,
                include_sources=include_sources
            )
            return {"results": results}
            
        except Exception as e:
            logger.error(f"Error processing batch query: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/clear-database")
    async def clear_database():
        """Clear the vector database"""
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        try:
            rag_system.clear_database()
            return {"message": "Database cleared successfully"}
            
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/docs-alternative")
    async def docs_alternative():
        """Alternative documentation endpoint"""
        return {
            "message": "Climate Intelligence Platform API Documentation",
            "endpoints": {
                "GET /": "Root endpoint",
                "GET /health": "Health check",
                "POST /query": "Query the RAG system",
                "POST /upload": "Upload and process documents",
                "POST /add-text": "Add raw text to RAG system",
                "GET /climate-data": "Get climate data for location",
                "GET /carbon-footprint": "Calculate carbon footprint",
                "GET /system-info": "Get system information",
                "POST /batch-query": "Process multiple queries",
                "DELETE /clear-database": "Clear vector database"
            },
            "example_usage": {
                "query": {
                    "url": "/query",
                    "method": "POST",
                    "body": {
                        "question": "What is ClimateIQ?",
                        "k": 5,
                        "include_sources": True
                    }
                },
                "climate_data": {
                    "url": "/climate-data?location=London&data_type=weather",
                    "method": "GET"
                }
            }
        }


# Error handlers
if app:
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)}
        )


# Run the application
if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower()
        )
    except ImportError:
        logger.error("uvicorn not available")
        print("Please install uvicorn to run the API server")
else:
    # For deployment
    application = app