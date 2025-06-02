"""Advanced RAG system with multiple vector database support"""

import os
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from .document_processor import DocumentProcessor
from .llm_manager import llm_manager, LLMProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """Abstract base class for vector databases"""
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        raise NotImplementedError
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def delete_collection(self) -> None:
        raise NotImplementedError


class ChromaVectorDB(VectorDatabase):
    """ChromaDB implementation"""
    
    def __init__(self, collection_name: str = "climate_intelligence", persist_directory: str = "./data/vectordb"):
        if not chromadb:
            raise ImportError("ChromaDB not available")
        
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Loaded existing ChromaDB collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Climate Intelligence Platform documents"}
            )
            logger.info(f"Created new ChromaDB collection: {collection_name}")
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Add document chunks to ChromaDB"""
        if not chunks:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk['content'])
            metadatas.append(chunk['metadata'])
            ids.append(f"{chunk['metadata'].get('source', 'unknown')}_{chunk['metadata'].get('chunk_id', i)}")
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(chunks)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    }
                    search_results.append(result)
            
            return search_results
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
    
    def delete_collection(self) -> None:
        """Delete the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted ChromaDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting ChromaDB collection: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'count': count,
                'type': 'ChromaDB'
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}


class RAGSystem:
    """Advanced Retrieval-Augmented Generation system"""
    
    def __init__(
        self,
        vector_db: Optional[VectorDatabase] = None,
        llm_provider: Optional[LLMProvider] = None,
        embedding_model: Optional[str] = None
    ):
        self.document_processor = DocumentProcessor()
        
        # Initialize vector database
        if vector_db is None:
            try:
                self.vector_db = ChromaVectorDB()
            except ImportError:
                logger.error("No vector database available")
                self.vector_db = None
        else:
            self.vector_db = vector_db
        
        # Initialize LLM
        self.llm_provider = llm_provider or llm_manager.default_provider
        self.llm = llm_manager.get_langchain_llm(self.llm_provider)
        
        # Initialize embedding model
        if SentenceTransformer and embedding_model:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = llm_manager.get_embedding_model()
        
        logger.info(f"RAG System initialized with provider: {self.llm_provider}")
    
    def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Add documents to the RAG system"""
        all_chunks = []
        processing_stats = {}
        
        for file_path in file_paths:
            try:
                if Path(file_path).name.lower() == 'readme.md':
                    chunks = self.document_processor.process_readme(file_path)
                else:
                    chunks = self.document_processor.process_file(file_path)
                
                all_chunks.extend(chunks)
                processing_stats[file_path] = len(chunks)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                processing_stats[file_path] = 0
        
        # Add to vector database
        if self.vector_db and all_chunks:
            self.vector_db.add_documents(all_chunks)
        
        stats = self.document_processor.get_processing_stats(all_chunks)
        stats['file_processing'] = processing_stats
        
        return stats
    
    def add_text(self, text: str, source: str = "text_input") -> Dict[str, Any]:
        """Add raw text to the RAG system"""
        chunks = self.document_processor.process_text(text, source)
        
        if self.vector_db and chunks:
            self.vector_db.add_documents(chunks)
        
        return self.document_processor.get_processing_stats(chunks)
    
    async def query(
        self,
        question: str,
        k: int = 5,
        include_sources: bool = True,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Query the RAG system"""
        
        if not self.vector_db:
            return {
                'answer': "Vector database not available",
                'sources': [],
                'error': "No vector database configured"
            }
        
        # Retrieve relevant documents
        relevant_docs = self.vector_db.search(question, k=k)
        
        if not relevant_docs:
            return {
                'answer': "No relevant documents found for your question.",
                'sources': [],
                'retrieved_docs': 0
            }
        
        # Prepare context
        context = self._prepare_context(relevant_docs)
        
        # Generate prompt
        prompt = self._create_prompt(question, context)
        
        # Generate answer
        try:
            answer = await llm_manager.generate_response(
                prompt,
                provider=self.llm_provider,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            answer = "I apologize, but I encountered an error while generating a response."
        
        # Prepare response
        response = {
            'answer': answer,
            'retrieved_docs': len(relevant_docs),
            'query': question
        }
        
        if include_sources:
            response['sources'] = self._format_sources(relevant_docs)
        
        return response
    
    def _prepare_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(relevant_docs):
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            # Add source information
            source = metadata.get('source', 'Unknown')
            section = metadata.get('section_title', '')
            
            context_part = f"[Source {i+1}: {source}"
            if section:
                context_part += f" - {section}"
            context_part += f"]\n{content}\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create prompt for the LLM"""
        prompt = f"""You are an AI assistant specialized in climate action and environmental intelligence. Use the following context to answer the user's question accurately and comprehensively.

Context:
{context}

Question: {question}

Instructions:
1. Base your answer primarily on the provided context
2. If the context doesn't contain enough information, clearly state what information is missing
3. Provide specific details and examples when available
4. If discussing technical concepts, explain them clearly
5. Focus on actionable insights related to climate action and environmental intelligence

Answer:"""
        
        return prompt
    
    def _format_sources(self, relevant_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for response"""
        sources = []
        
        for doc in relevant_docs:
            metadata = doc.get('metadata', {})
            source_info = {
                'source': metadata.get('source', 'Unknown'),
                'section': metadata.get('section_title', ''),
                'chunk_id': metadata.get('chunk_id', 0),
                'relevance_score': 1.0 - doc.get('distance', 0.0)  # Convert distance to relevance
            }
            sources.append(source_info)
        
        return sources
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the RAG system"""
        info = {
            'llm_provider': str(self.llm_provider) if self.llm_provider else None,
            'available_providers': [str(p) for p in llm_manager.get_available_providers()],
            'embedding_model': str(type(self.embedding_model).__name__) if self.embedding_model else None,
            'vector_db_type': type(self.vector_db).__name__ if self.vector_db else None
        }
        
        if self.vector_db and hasattr(self.vector_db, 'get_collection_info'):
            info['collection_info'] = self.vector_db.get_collection_info()
        
        return info
    
    def clear_database(self) -> None:
        """Clear the vector database"""
        if self.vector_db:
            self.vector_db.delete_collection()
            logger.info("Vector database cleared")
    
    async def batch_query(
        self,
        questions: List[str],
        k: int = 5,
        include_sources: bool = False
    ) -> List[Dict[str, Any]]:
        """Process multiple queries in batch"""
        tasks = [
            self.query(question, k=k, include_sources=include_sources)
            for question in questions
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'answer': f"Error processing question: {str(result)}",
                    'sources': [],
                    'error': str(result),
                    'query': questions[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results