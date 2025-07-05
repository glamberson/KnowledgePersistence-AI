# Reference Documentation Module (RDM)

## Modular Design Philosophy

**Purpose**: Standalone reference documentation system that can be used independently or integrated with other systems (KnowledgePersistence-AI, CMS projects, etc.)

**Key Principles**:
- **Complete Independence**: Functions without external dependencies
- **Pluggable Architecture**: Easy integration with existing systems
- **Configurable Storage**: Multiple database backends supported
- **API-First Design**: RESTful API for external integration
- **Docker Containerized**: Easy deployment and scaling

## Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                Reference Documentation Module (RDM)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   RDM Core      │  │   RDM API       │  │   RDM Admin     │  │
│  │                 │  │                 │  │                 │  │
│  │ • Document      │  │ • REST API      │  │ • CLI Tools     │  │
│  │   Storage       │  │ • Search API    │  │ • Web UI        │  │
│  │ • Search Engine │  │ • Analytics API │  │ • Monitoring    │  │
│  │ • Analysis      │  │ • Integration   │  │ • Maintenance   │  │
│  │   Engine        │  │   Webhooks      │  │                 │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                      │                      │        │
│           └──────────────────────┼──────────────────────┘        │
│                                  │                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    Storage Layer                            │  │
│  │                                                             │  │
│  │ • PostgreSQL (primary)                                     │  │
│  │ • SQLite (development/embedded)                             │  │
│  │ • File System (backup/export)                              │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Standalone Module Structure

```
reference-documentation-module/
├── rdm/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── document_manager.py
│   │   ├── search_engine.py
│   │   ├── analysis_engine.py
│   │   └── content_loader.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── postgres_backend.py
│   │   ├── sqlite_backend.py
│   │   └── base_backend.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── rest_api.py
│   │   ├── search_api.py
│   │   └── analytics_api.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── web_ui.py
│   │   └── monitoring.py
│   └── integrations/
│       ├── __init__.py
│       ├── knowledge_persistence.py
│       ├── cms_integration.py
│       └── webhook_handlers.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
├── config/
│   ├── default.yaml
│   ├── production.yaml
│   └── development.yaml
├── tests/
│   ├── test_core/
│   ├── test_api/
│   └── test_integrations/
├── docs/
│   ├── api.md
│   ├── integration.md
│   └── deployment.md
├── requirements.txt
├── setup.py
├── README.md
└── VERSION
```

## Core Module Implementation

### Document Manager (rdm/core/document_manager.py)

```python
"""
Reference Documentation Module - Core Document Manager
Handles document storage, retrieval, and management
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class ReferenceDocument:
    """Reference document data structure"""
    id: str
    collection_id: str
    title: str
    section_path: str
    content: str
    content_type: str
    content_hash: str
    word_count: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ReferenceCollection:
    """Reference collection data structure"""
    id: str
    name: str
    description: str
    version: str
    source_url: Optional[str]
    collection_type: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    metadata: Dict[str, Any]

class DocumentManager:
    """Core document management functionality"""
    
    def __init__(self, storage_backend, config=None):
        self.storage = storage_backend
        self.config = config or {}
        self.content_hasher = ContentHasher()
        
    async def create_collection(self, collection_data: Dict[str, Any]) -> ReferenceCollection:
        """Create a new reference collection"""
        collection_id = self._generate_id()
        
        collection = ReferenceCollection(
            id=collection_id,
            name=collection_data['name'],
            description=collection_data.get('description', ''),
            version=collection_data.get('version', '1.0'),
            source_url=collection_data.get('source_url'),
            collection_type=collection_data.get('collection_type', 'manual'),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
            metadata=collection_data.get('metadata', {})
        )
        
        await self.storage.save_collection(collection)
        return collection
    
    async def add_document(self, document_data: Dict[str, Any]) -> ReferenceDocument:
        """Add a document to a collection"""
        document_id = self._generate_id()
        content_hash = self.content_hasher.calculate_hash(document_data['content'])
        
        # Check for existing document with same hash
        existing_doc = await self.storage.get_document_by_hash(content_hash)
        if existing_doc:
            return existing_doc
        
        document = ReferenceDocument(
            id=document_id,
            collection_id=document_data['collection_id'],
            title=document_data['title'],
            section_path=document_data.get('section_path', ''),
            content=document_data['content'],
            content_type=document_data.get('content_type', 'text'),
            content_hash=content_hash,
            word_count=len(document_data['content'].split()),
            metadata=document_data.get('metadata', {}),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await self.storage.save_document(document)
        return document
    
    async def get_collection(self, collection_id: str) -> Optional[ReferenceCollection]:
        """Get collection by ID"""
        return await self.storage.get_collection(collection_id)
    
    async def get_document(self, document_id: str) -> Optional[ReferenceDocument]:
        """Get document by ID"""
        return await self.storage.get_document(document_id)
    
    async def list_collections(self, active_only: bool = True) -> List[ReferenceCollection]:
        """List all collections"""
        return await self.storage.list_collections(active_only)
    
    async def list_documents(self, collection_id: str) -> List[ReferenceDocument]:
        """List documents in a collection"""
        return await self.storage.list_documents(collection_id)
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())

class ContentHasher:
    """Content hashing utility"""
    
    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
```

### Content Loader (rdm/core/content_loader.py)

```python
"""
Reference Documentation Module - Content Loader
Handles loading documentation from various sources
"""

import aiohttp
import asyncio
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import re

class ContentLoader:
    """Load content from various sources"""
    
    def __init__(self, document_manager):
        self.document_manager = document_manager
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def load_python_documentation(self, version: str = "3.13") -> ReferenceCollection:
        """Load Python documentation"""
        print(f"Loading Python {version} documentation...")
        
        # Create collection
        collection = await self.document_manager.create_collection({
            'name': f'python_{version}_manual',
            'description': f'Python {version} Official Documentation',
            'version': version,
            'source_url': f'https://docs.python.org/{version}/',
            'collection_type': 'manual',
            'metadata': {
                'language': 'python',
                'doc_type': 'official',
                'auto_loaded': True
            }
        })
        
        # Load Python documentation sections
        python_sections = await self._fetch_python_sections(version)
        
        # Process each section
        for section in python_sections:
            await self.document_manager.add_document({
                'collection_id': collection.id,
                'title': section['title'],
                'section_path': section['path'],
                'content': section['content'],
                'content_type': 'text',
                'metadata': section.get('metadata', {})
            })
        
        print(f"Loaded {len(python_sections)} Python documentation sections")
        return collection
    
    async def load_postgresql_documentation(self, version: str = "17") -> ReferenceCollection:
        """Load PostgreSQL documentation"""
        print(f"Loading PostgreSQL {version} documentation...")
        
        # Create collection
        collection = await self.document_manager.create_collection({
            'name': f'postgresql_{version}_manual',
            'description': f'PostgreSQL {version} Official Documentation',
            'version': version,
            'source_url': f'https://www.postgresql.org/docs/{version}/',
            'collection_type': 'manual',
            'metadata': {
                'database': 'postgresql',
                'doc_type': 'official',
                'auto_loaded': True
            }
        })
        
        # Load PostgreSQL documentation sections
        postgres_sections = await self._fetch_postgres_sections(version)
        
        # Process each section
        for section in postgres_sections:
            await self.document_manager.add_document({
                'collection_id': collection.id,
                'title': section['title'],
                'section_path': section['path'],
                'content': section['content'],
                'content_type': 'text',
                'metadata': section.get('metadata', {})
            })
        
        print(f"Loaded {len(postgres_sections)} PostgreSQL documentation sections")
        return collection
    
    async def load_methodology_documentation(self) -> ReferenceCollection:
        """Load project management and methodology documentation"""
        print("Loading methodology documentation...")
        
        # Create collection
        collection = await self.document_manager.create_collection({
            'name': 'pm_methodologies',
            'description': 'Project Management Methodologies and Best Practices',
            'version': '1.0',
            'collection_type': 'methodology',
            'metadata': {
                'domain': 'project_management',
                'doc_type': 'methodology',
                'auto_loaded': True
            }
        })
        
        # Load methodology content
        methodologies = await self._load_methodology_content()
        
        # Process each methodology
        for methodology in methodologies:
            for section in methodology['sections']:
                await self.document_manager.add_document({
                    'collection_id': collection.id,
                    'title': section['title'],
                    'section_path': f"{methodology['name']}/{section['path']}",
                    'content': section['content'],
                    'content_type': 'text',
                    'metadata': {
                        'methodology': methodology['name'],
                        'category': section.get('category', 'general'),
                        'importance': section.get('importance', 'medium')
                    }
                })
        
        total_sections = sum(len(m['sections']) for m in methodologies)
        print(f"Loaded {total_sections} methodology sections")
        return collection
    
    async def _fetch_python_sections(self, version: str) -> List[Dict[str, Any]]:
        """Fetch Python documentation sections"""
        # This would implement actual web scraping or API calls
        # For now, return structured content
        return [
            {
                'title': 'Built-in Functions',
                'path': 'library/functions',
                'content': self._get_python_builtin_functions_content(),
                'metadata': {'category': 'library', 'importance': 'high'}
            },
            {
                'title': 'Data Types',
                'path': 'library/datatypes',
                'content': self._get_python_datatypes_content(),
                'metadata': {'category': 'library', 'importance': 'high'}
            },
            {
                'title': 'Control Flow',
                'path': 'tutorial/controlflow',
                'content': self._get_python_controlflow_content(),
                'metadata': {'category': 'tutorial', 'importance': 'high'}
            },
            {
                'title': 'Error Handling',
                'path': 'tutorial/errors',
                'content': self._get_python_errors_content(),
                'metadata': {'category': 'tutorial', 'importance': 'high'}
            },
            {
                'title': 'File I/O',
                'path': 'tutorial/inputoutput',
                'content': self._get_python_fileio_content(),
                'metadata': {'category': 'tutorial', 'importance': 'medium'}
            }
        ]
    
    async def _fetch_postgres_sections(self, version: str) -> List[Dict[str, Any]]:
        """Fetch PostgreSQL documentation sections"""
        return [
            {
                'title': 'SQL Commands',
                'path': 'sql-commands',
                'content': self._get_postgres_sql_commands_content(),
                'metadata': {'category': 'reference', 'importance': 'high'}
            },
            {
                'title': 'Data Types',
                'path': 'datatype',
                'content': self._get_postgres_datatypes_content(),
                'metadata': {'category': 'reference', 'importance': 'high'}
            },
            {
                'title': 'Functions and Operators',
                'path': 'functions',
                'content': self._get_postgres_functions_content(),
                'metadata': {'category': 'reference', 'importance': 'high'}
            },
            {
                'title': 'Indexes',
                'path': 'indexes',
                'content': self._get_postgres_indexes_content(),
                'metadata': {'category': 'performance', 'importance': 'medium'}
            },
            {
                'title': 'Performance Tips',
                'path': 'performance-tips',
                'content': self._get_postgres_performance_content(),
                'metadata': {'category': 'performance', 'importance': 'medium'}
            }
        ]
    
    async def _load_methodology_content(self) -> List[Dict[str, Any]]:
        """Load methodology content"""
        return [
            {
                'name': 'agile',
                'sections': [
                    {
                        'title': 'Agile Principles',
                        'path': 'principles',
                        'content': self._get_agile_principles_content(),
                        'category': 'foundation',
                        'importance': 'high'
                    },
                    {
                        'title': 'User Stories',
                        'path': 'user_stories',
                        'content': self._get_user_stories_content(),
                        'category': 'planning',
                        'importance': 'high'
                    },
                    {
                        'title': 'Sprint Planning',
                        'path': 'sprint_planning',
                        'content': self._get_sprint_planning_content(),
                        'category': 'execution',
                        'importance': 'high'
                    }
                ]
            },
            {
                'name': 'scrum',
                'sections': [
                    {
                        'title': 'Scrum Framework',
                        'path': 'framework',
                        'content': self._get_scrum_framework_content(),
                        'category': 'foundation',
                        'importance': 'high'
                    },
                    {
                        'title': 'Scrum Events',
                        'path': 'events',
                        'content': self._get_scrum_events_content(),
                        'category': 'execution',
                        'importance': 'high'
                    }
                ]
            },
            {
                'name': 'risk_management',
                'sections': [
                    {
                        'title': 'Risk Identification',
                        'path': 'identification',
                        'content': self._get_risk_identification_content(),
                        'category': 'analysis',
                        'importance': 'high'
                    },
                    {
                        'title': 'Risk Assessment',
                        'path': 'assessment',
                        'content': self._get_risk_assessment_content(),
                        'category': 'analysis',
                        'importance': 'high'
                    }
                ]
            }
        ]
    
    def _get_python_builtin_functions_content(self) -> str:
        """Get Python built-in functions content"""
        return """
# Python Built-in Functions

Python provides numerous built-in functions that are always available without importing any modules.

## Common Built-in Functions

### Data Type Functions
- `int()` - Convert to integer
- `float()` - Convert to float
- `str()` - Convert to string
- `bool()` - Convert to boolean
- `list()` - Create list
- `dict()` - Create dictionary
- `set()` - Create set
- `tuple()` - Create tuple

### Sequence Functions
- `len()` - Get length of sequence
- `range()` - Generate sequence of numbers
- `enumerate()` - Add counter to iterable
- `zip()` - Combine iterables
- `sorted()` - Return sorted list
- `reversed()` - Return reversed iterator

### Math Functions
- `abs()` - Absolute value
- `min()` - Minimum value
- `max()` - Maximum value
- `sum()` - Sum of sequence
- `round()` - Round to nearest integer

### I/O Functions
- `print()` - Print to stdout
- `input()` - Read from stdin
- `open()` - Open file

### Inspection Functions
- `type()` - Get object type
- `isinstance()` - Check if object is instance
- `hasattr()` - Check if object has attribute
- `getattr()` - Get attribute value
- `setattr()` - Set attribute value
- `dir()` - List object attributes

### Functional Programming
- `map()` - Apply function to iterable
- `filter()` - Filter iterable
- `any()` - Check if any element is True
- `all()` - Check if all elements are True
"""

    def _get_postgres_sql_commands_content(self) -> str:
        """Get PostgreSQL SQL commands content"""
        return """
# PostgreSQL SQL Commands

PostgreSQL supports standard SQL commands plus many extensions.

## Data Definition Language (DDL)

### CREATE Commands
- `CREATE TABLE` - Create new table
- `CREATE INDEX` - Create index
- `CREATE VIEW` - Create view
- `CREATE FUNCTION` - Create function
- `CREATE PROCEDURE` - Create procedure
- `CREATE TRIGGER` - Create trigger

### ALTER Commands
- `ALTER TABLE` - Modify table structure
- `ALTER INDEX` - Modify index
- `ALTER VIEW` - Modify view

### DROP Commands
- `DROP TABLE` - Remove table
- `DROP INDEX` - Remove index
- `DROP VIEW` - Remove view

## Data Manipulation Language (DML)

### SELECT Command
- `SELECT` - Query data
- `FROM` - Specify tables
- `WHERE` - Filter conditions
- `GROUP BY` - Group results
- `HAVING` - Filter groups
- `ORDER BY` - Sort results
- `LIMIT` - Limit results
- `OFFSET` - Skip results

### INSERT Command
- `INSERT INTO` - Add new records
- `VALUES` - Specify values
- `SELECT` - Insert from query

### UPDATE Command
- `UPDATE` - Modify existing records
- `SET` - Specify new values
- `WHERE` - Filter records

### DELETE Command
- `DELETE FROM` - Remove records
- `WHERE` - Filter records

## PostgreSQL-Specific Features

### UPSERT
- `INSERT ... ON CONFLICT` - Insert or update

### Array Operations
- `ARRAY[...]` - Array literal
- `ANY()` - Match any array element
- `ALL()` - Match all array elements

### JSON Operations
- `->` - Get JSON field
- `->>` - Get JSON field as text
- `@>` - Contains JSON
- `<@` - Contained in JSON

### Window Functions
- `ROW_NUMBER()` - Row number
- `RANK()` - Rank with gaps
- `DENSE_RANK()` - Rank without gaps
- `LAG()` - Previous row value
- `LEAD()` - Next row value

### Common Table Expressions (CTE)
- `WITH` - Define CTE
- `RECURSIVE` - Recursive CTE
"""

    def _get_agile_principles_content(self) -> str:
        """Get Agile principles content"""
        return """
# Agile Principles

The Agile Manifesto defines the core values and principles of Agile software development.

## Four Core Values

1. **Individuals and interactions** over processes and tools
2. **Working software** over comprehensive documentation
3. **Customer collaboration** over contract negotiation
4. **Responding to change** over following a plan

## Twelve Principles

1. **Customer satisfaction** through early and continuous delivery of valuable software
2. **Welcome changing requirements**, even late in development
3. **Deliver working software frequently**, with preference for shorter timescales
4. **Business people and developers** must work together daily throughout the project
5. **Build projects around motivated individuals**. Give them the environment and support they need, and trust them to get the job done
6. **Face-to-face conversation** is the most efficient and effective method of conveying information
7. **Working software** is the primary measure of progress
8. **Sustainable development** - maintain constant pace indefinitely
9. **Technical excellence** and good design enhances agility
10. **Simplicity** - the art of maximizing the amount of work not done
11. **Self-organizing teams** produce the best architectures, requirements, and designs
12. **Regular reflection** on how to become more effective, then tune and adjust behavior accordingly

## Key Practices

### Planning
- User Stories
- Story Points
- Sprint Planning
- Release Planning

### Development
- Test-Driven Development (TDD)
- Continuous Integration
- Pair Programming
- Refactoring

### Collaboration
- Daily Standups
- Sprint Reviews
- Retrospectives
- Cross-functional Teams

### Delivery
- Frequent Releases
- Continuous Deployment
- Feedback Loops
- Minimum Viable Product (MVP)
"""
```

## REST API Interface (rdm/api/rest_api.py)

```python
"""
Reference Documentation Module - REST API
Provides RESTful API for external integration
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uvicorn

from ..core.document_manager import DocumentManager
from ..core.search_engine import SearchEngine
from ..core.analysis_engine import AnalysisEngine

app = FastAPI(
    title="Reference Documentation Module API",
    description="API for managing and searching reference documentation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
async def get_document_manager() -> DocumentManager:
    # This would be configured based on settings
    from ..storage.postgres_backend import PostgresBackend
    storage = PostgresBackend()
    return DocumentManager(storage)

async def get_search_engine() -> SearchEngine:
    # This would be configured based on settings
    return SearchEngine()

async def get_analysis_engine() -> AnalysisEngine:
    # This would be configured based on settings
    return AnalysisEngine()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Reference Documentation Module API", "version": "1.0.0"}

@app.get("/collections")
async def list_collections(
    active_only: bool = Query(True, description="Only return active collections"),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """List all collections"""
    collections = await doc_manager.list_collections(active_only)
    return {"collections": [asdict(c) for c in collections]}

@app.get("/collections/{collection_id}")
async def get_collection(
    collection_id: str,
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Get collection by ID"""
    collection = await doc_manager.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"collection": asdict(collection)}

@app.get("/collections/{collection_id}/documents")
async def list_documents(
    collection_id: str,
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """List documents in collection"""
    documents = await doc_manager.list_documents(collection_id)
    return {"documents": [asdict(d) for d in documents]}

@app.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Get document by ID"""
    document = await doc_manager.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": asdict(document)}

@app.post("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    collections: Optional[List[str]] = Query(None, description="Collections to search"),
    limit: int = Query(10, description="Maximum results"),
    search_engine: SearchEngine = Depends(get_search_engine)
):
    """Search documents"""
    results = await search_engine.search(
        query=query,
        collections=collections,
        limit=limit
    )
    return {"results": results}

@app.get("/documents/{document_id}/analysis")
async def get_document_analysis(
    document_id: str,
    analysis_type: Optional[str] = Query(None, description="Type of analysis"),
    analysis_engine: AnalysisEngine = Depends(get_analysis_engine)
):
    """Get document analysis"""
    analysis = await analysis_engine.get_document_analysis(
        document_id, analysis_type
    )
    return {"analysis": analysis}

@app.post("/load/python")
async def load_python_docs(
    version: str = Query("3.13", description="Python version"),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Load Python documentation"""
    from ..core.content_loader import ContentLoader
    
    async with ContentLoader(doc_manager) as loader:
        collection = await loader.load_python_documentation(version)
    
    return {"message": f"Python {version} documentation loaded", "collection_id": collection.id}

@app.post("/load/postgresql")
async def load_postgresql_docs(
    version: str = Query("17", description="PostgreSQL version"),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Load PostgreSQL documentation"""
    from ..core.content_loader import ContentLoader
    
    async with ContentLoader(doc_manager) as loader:
        collection = await loader.load_postgresql_documentation(version)
    
    return {"message": f"PostgreSQL {version} documentation loaded", "collection_id": collection.id}

@app.post("/load/methodologies")
async def load_methodologies(
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Load methodology documentation"""
    from ..core.content_loader import ContentLoader
    
    async with ContentLoader(doc_manager) as loader:
        collection = await loader.load_methodology_documentation()
    
    return {"message": "Methodology documentation loaded", "collection_id": collection.id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Integration Interface (rdm/integrations/knowledge_persistence.py)

```python
"""
Reference Documentation Module - KnowledgePersistence-AI Integration
Provides integration with the main KnowledgePersistence-AI system
"""

from typing import Dict, List, Any, Optional
import asyncio

class KnowledgePersistenceIntegration:
    """Integration with KnowledgePersistence-AI system"""
    
    def __init__(self, rdm_api_url: str, kp_database_config: Dict[str, Any]):
        self.rdm_api_url = rdm_api_url
        self.kp_database_config = kp_database_config
        self.reference_enhancer = ReferenceEnhancer()
        
    async def enhance_adaptive_response(self, 
                                      user_query: str, 
                                      adaptive_response: Dict[str, Any],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance adaptive response with reference materials"""
        
        # Search for relevant reference materials
        relevant_references = await self.search_relevant_references(
            user_query, context
        )
        
        # Enhance response with references
        enhanced_response = await self.reference_enhancer.enhance_response(
            adaptive_response, relevant_references
        )
        
        # Create cross-links
        await self.create_cross_links(
            user_query, adaptive_response, relevant_references
        )
        
        return enhanced_response
    
    async def search_relevant_references(self, 
                                       query: str, 
                                       context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for relevant reference materials"""
        import aiohttp
        
        # Determine relevant collections based on context
        collections = self._determine_relevant_collections(context)
        
        # Search RDM API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.rdm_api_url}/search",
                params={
                    'query': query,
                    'collections': collections,
                    'limit': 5
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
                
        return []
    
    def _determine_relevant_collections(self, context: Dict[str, Any]) -> List[str]:
        """Determine relevant collections based on context"""
        collections = []
        
        # Check for coding context
        if context.get('coding_focus', 0) > 0.5:
            collections.extend(['python_3.13_manual', 'postgresql_17_manual'])
        
        # Check for project management context
        if context.get('domain_classification', {}).get('primary') == 'project_management':
            collections.append('pm_methodologies')
        
        # Check for specific technology mentions
        keywords = context.get('keywords', [])
        if 'python' in keywords:
            collections.append('python_3.13_manual')
        if any(kw in keywords for kw in ['postgresql', 'postgres', 'sql']):
            collections.append('postgresql_17_manual')
        
        return collections
    
    async def create_cross_links(self, 
                               query: str,
                               adaptive_response: Dict[str, Any],
                               references: List[Dict[str, Any]]):
        """Create cross-links between adaptive knowledge and references"""
        # This would implement the cross-linking logic
        # connecting adaptive patterns with reference materials
        pass

class ReferenceEnhancer:
    """Enhances responses with reference materials"""
    
    async def enhance_response(self, 
                             adaptive_response: Dict[str, Any],
                             references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance response with reference materials"""
        
        if not references:
            return adaptive_response
        
        # Add reference section
        enhanced_response = {
            'adaptive_response': adaptive_response,
            'reference_materials': {
                'count': len(references),
                'references': []
            }
        }
        
        # Process each reference
        for ref in references:
            reference_info = {
                'title': ref.get('title', ''),
                'collection': ref.get('collection_name', ''),
                'section': ref.get('section_path', ''),
                'excerpt': ref.get('content', '')[:200] + '...',
                'relevance_score': ref.get('similarity_score', 0.0)
            }
            
            enhanced_response['reference_materials']['references'].append(reference_info)
        
        return enhanced_response
```

## Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "rdm.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  rdm-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/rdm
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./config:/app/config

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=rdm
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

This modular design provides:

1. **Complete Independence**: Runs standalone with its own database and API
2. **Easy Integration**: Simple REST API for integration with other systems
3. **Docker Deployment**: Containerized for easy deployment
4. **Configurable**: Support for different backends and configurations
5. **Extensible**: Easy to add new content types and analysis features

Perfect for your CMS project or any system that needs authoritative reference documentation with intelligent search and analysis capabilities!

