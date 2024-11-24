## Directory Tree
```
.
├── Makefile
├── README.md
├── TO DO.md
├── app
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   └── main.cpython-312.pyc
│   ├── api
│   │   ├── __pycache__
│   │   │   ├── routes.cpython-312.pyc
│   │   │   └── schemas.cpython-312.pyc
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── main.py
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── main.js
│   └── templates
│       ├── about.html
│       ├── base.html
│       ├── chat.html
│       ├── execute.html
│       ├── index.html
│       ├── settings.html
│       └── tenders.html
├── db.sqlite3
├── main.py
├── requirements.txt
├── resume_repo.py
├── resumed_repo.md
├── run.py
└── src
    ├── __init__.py
    ├── __pycache__
    │   └── __init__.cpython-312.pyc
    ├── api
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-312.pyc
    │   │   └── public_market_api.cpython-312.pyc
    │   └── public_market_api.py
    ├── config
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-312.pyc
    │   │   └── settings.cpython-312.pyc
    │   └── settings.py
    ├── database
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-312.pyc
    │   │   ├── base.cpython-312.pyc
    │   │   └── repository.cpython-312.pyc
    │   ├── base.py
    │   └── repository.py
    ├── models
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-312.pyc
    │   │   ├── enum.cpython-312.pyc
    │   │   ├── keywords.cpython-312.pyc
    │   │   └── tender.cpython-312.pyc
    │   ├── enum.py
    │   ├── keywords.py
    │   └── tender.py
    └── utils
        ├── __init__.py
        ├── __pycache__
        │   ├── __init__.cpython-312.pyc
        │   ├── logger.cpython-312.pyc
        │   └── safe_load.cpython-312.pyc
        ├── logger.py
        └── safe_load.py

21 directories, 56 files

```

### ./run.py
```python
import uvicorn
from src.database.base import get_db, init_db
from src.api.public_market_api import PublicMarketAPI
from src.database.repository import TenderRepository, KeywordRepository
from src.utils.logger import setup_logger

if __name__ == "__main__":

    logger = setup_logger(__name__)

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Initialize API
    logger.info("Initializing API client...")
    api = PublicMarketAPI()

    # Get database session
    db = next(get_db())
    tender_repo = TenderRepository(db)
    keyword_repo = KeywordRepository(db)

    # Initialize default keywords if needed
    keyword_repo.initialize_default_keywords()

    uvicorn.run("app.main:app", 
                host="0.0.0.0", 
                port=5353, 
                reload=True)

```

### ./README.md
```text
# mercadopublico-monitoring
```

### ./main.py
```python
from src.api.public_market_api import PublicMarketAPI
from src.database.base import get_db, init_db
from src.database.repository import TenderRepository, KeywordRepository
from src.models.keywords import KeywordType
from src.utils.logger import setup_logger
from typing import List, Tuple


def get_keywords(repo: KeywordRepository) -> Tuple[List[str], List[str]]:
    """
    Get include and exclude keywords from the database
    
    Args:
        repo: KeywordRepository instance
        
    Returns:
        Tuple[List[str], List[str]]: Lists of include and exclude keywords
    """
    include_keywords = [k.keyword for k in repo.get_keywords_by_type(KeywordType.INCLUDE)]
    exclude_keywords = [k.keyword for k in repo.get_keywords_by_type(KeywordType.EXCLUDE)]
    return include_keywords, exclude_keywords


def main():
    # Setup logging
    logger = setup_logger(__name__)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()

        # Initialize API
        logger.info("Initializing API client...")
        api = PublicMarketAPI()

        # Get database session
        db = next(get_db())
        tender_repo = TenderRepository(db)
        keyword_repo = KeywordRepository(db)

        # Initialize default keywords if needed
        keyword_repo.initialize_default_keywords()

        # Get keywords from database
        include_keywords, exclude_keywords = get_keywords(keyword_repo)
        
        logger.info(f"Using include keywords: {include_keywords}")
        logger.info(f"Using exclude keywords: {exclude_keywords}")

        # Search tenders
        tenders = api.search_tenders(
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
            days_back=2
        )

        # Save to database
        new_tenders = 0
        updated_tenders = 0
        unchanged_tenders = 0
        
        for tender in tenders:
            try:
                existing_tender = tender_repo.get_tender_by_code(tender.code)
                
                if existing_tender:
                    # Update existing tender
                    updated_tender = tender_repo.update_tender(tender)
                    if updated_tender.updated_at > existing_tender.updated_at:
                        updated_tenders += 1
                    else:
                        unchanged_tenders += 1
                else:
                    # Create new tender
                    tender_repo.create_tender(tender)
                    new_tenders += 1
                    
            except Exception as e:
                logger.error(f"Error processing tender {tender.code}: {str(e)}")
                continue

            logger.info(f"Successfully processed {len(tenders)} tenders")
            logger.info(f"New tenders: {new_tenders}")
            logger.info(f"Updated tenders: {updated_tenders}")
            logger.info(f"Unchanged tenders: {unchanged_tenders}")

    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise
    finally:
        logger.info("Process completed")


if __name__ == "__main__":
    main()

```

### ./app/__init__.py
```python

```

### ./app/main.py
```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router as api_router

app = FastAPI(title="Mercado Público Monitor")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(api_router, prefix="/api")

# Web routes
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/tenders")
async def tenders(request: Request):
    return templates.TemplateResponse("tenders.html", {"request": request})

@app.get("/chat")
async def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/settings")
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/execute")
async def execute(request: Request):
    return templates.TemplateResponse("execute.html", {"request": request})

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5353)

```

### ./app/api/schemas.py
```python
# app/api/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class KeywordUpdate(BaseModel):
    """
    Schema for updating keywords
    
    Attributes:
        include_keywords: List of keywords to include in searches
        exclude_keywords: List of keywords to exclude from searches
    """
    include_keywords: List[str] = Field(
        default=[],
        description="List of keywords to include in searches"
    )
    exclude_keywords: List[str] = Field(
        default=[],
        description="List of keywords to exclude from searches"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "include_keywords": ["software", "desarrollo", "tecnología"],
                "exclude_keywords": ["limpieza", "mantenimiento"]
            }
        }
    )

class ExecuteRequest(BaseModel):
    """
    Schema for execution request
    
    Attributes:
        days: Number of days to look back for tenders
    """
    days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to look back for tenders"
    )

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "days": 30
            }
        }
    )

class TenderResponse(BaseModel):
    """
    Schema for tender response
    
    Attributes:
        code: Unique identifier for the tender
        name: Name or title of the tender
        status: Current status of the tender
        organization: Organization that created the tender
        closing_date: Deadline for tender submissions
        estimated_amount: Estimated budget for the tender
        tender_type: Type of tender based on amount
    """
    code: str = Field(..., description="Unique identifier for the tender")
    name: str = Field(..., description="Name or title of the tender")
    status: str = Field(..., description="Current status of the tender")
    organization: Optional[str] = Field(None, description="Organization that created the tender")
    closing_date: Optional[datetime] = Field(None, description="Deadline for tender submissions")
    estimated_amount: Optional[float] = Field(None, description="Estimated budget for the tender")
    tender_type: Optional[str] = Field(None, description="Type of tender based on amount")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class KeywordBase(BaseModel):
    """
    Base schema for keywords
    
    Attributes:
        keyword: The keyword text
        type: Type of keyword (include/exclude)
    """
    keyword: str = Field(..., description="The keyword text")
    type: str = Field(..., description="Type of keyword (include/exclude)")

class KeywordCreate(KeywordBase):
    """Schema for creating a new keyword"""
    pass

class KeywordResponse(KeywordBase):
    """
    Schema for keyword response
    
    Attributes:
        id: Unique identifier for the keyword
    """
    id: int = Field(..., description="Unique identifier for the keyword")

    model_config = ConfigDict(
        from_attributes=True
    )

```

### ./app/api/routes.py
```python
# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database.base import get_db
from src.database.repository import TenderRepository, KeywordRepository, KeywordType
from .schemas import TenderResponse, KeywordResponse, KeywordCreate, ExecuteRequest
from src.api.public_market_api import PublicMarketAPI
from fastapi import BackgroundTasks

# Import logger from src.utils 
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/tenders", response_model=List[TenderResponse])
async def get_tenders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get tenders with optional filtering
    """
    try:
        repo = TenderRepository(db)
        if any([search, status, start_date, end_date]):
            tenders = repo.get_tenders_with_filters(
                skip=skip,
                limit=limit,
                search=search,
                status=status,
                start_date=start_date,
                end_date=end_date
            )
        else:
            tenders = repo.get_all_tenders()
            
        # Convertir los objetos SQLAlchemy a diccionarios y luego a modelos Pydantic
        return [TenderResponse.model_validate(tender) for tender in tenders]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keywords", response_model=List[KeywordResponse])
async def get_keywords(db: Session = Depends(get_db)):
    """Get all keywords"""
    try:
        repo = KeywordRepository(db)
        keywords = repo.get_all_keywords()
        return [KeywordResponse.model_validate(k) for k in keywords]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keywords", response_model=KeywordResponse)
async def create_keyword(
    keyword: KeywordCreate,
    db: Session = Depends(get_db)
):
    """Create a new keyword"""
    try:
        repo = KeywordRepository(db)
        new_keyword = repo.create_keyword(keyword.keyword, KeywordType(keyword.type))
        return KeywordResponse.model_validate(new_keyword)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/keywords/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """Delete a keyword"""
    try:
        repo = KeywordRepository(db)
        success = repo.delete_keyword(keyword_id)
        if not success:
            raise HTTPException(status_code=404, detail="Keyword not found")
        return {"message": "Keyword deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/keywords/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword: KeywordCreate,
    db: Session = Depends(get_db)
):
    """Update a keyword"""
    try:
        repo = KeywordRepository(db)
        updated_keyword = repo.update_keyword(
            keyword_id, 
            new_keyword=keyword.keyword, 
            new_type=KeywordType(keyword.type)
        )
        if not updated_keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")
        return KeywordResponse.model_validate(updated_keyword)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_search(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute tender search with specified parameters"""
    try:
        # Initialize repositories
        tender_repo = TenderRepository(db)
        keyword_repo = KeywordRepository(db)
        
        # Get keywords
        include_keywords = [k.keyword for k in keyword_repo.get_keywords_by_type(KeywordType.INCLUDE)]
        exclude_keywords = [k.keyword for k in keyword_repo.get_keywords_by_type(KeywordType.EXCLUDE)]
        
        # Initialize API
        api = PublicMarketAPI()
        
        # Add search task to background tasks
        background_tasks.add_task(
            process_search,
            api,
            include_keywords,
            exclude_keywords,
            request.days,
            tender_repo
        )
        
        return {
            "message": "Search started successfully",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting search: {str(e)}"
        )

async def process_search(
    api: PublicMarketAPI,
    include_keywords: List[str],
    exclude_keywords: List[str],
    days: int,
    tender_repo: TenderRepository
):
    """Process search in background"""
    try:
        tenders = api.search_tenders(
            include_keywords=include_keywords,
            exclude_keywords=exclude_keywords,
            days_back=days
        )
        
        new_count = 0
        updated_count = 0
        
        for tender in tenders:
            existing = tender_repo.get_tender_by_code(tender.code)
            if existing:
                tender_repo.update_tender(tender)
                updated_count += 1
            else:
                tender_repo.create_tender(tender)
                new_count += 1
                
    except Exception as e:
        logger.error(f"Error in background search: {str(e)}")

```

### ./app/templates/index.html
```text
{% extends "base.html" %}

{% block title %}Inicio - Mercado Público Monitor{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h1 class="card-title">Bienvenido a Mercado Público Monitor</h1>
        <p class="card-text">
            Esta aplicación te permite monitorear las licitaciones públicas de Chile que coincidan
            con tus criterios de búsqueda.
        </p>
        <div class="row mt-4">
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Búsqueda Inteligente</h5>
                        <p class="card-text">Configura palabras clave para encontrar las licitaciones relevantes para tu negocio.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Monitoreo Continuo</h5>
                        <p class="card-text">Mantente al día con las últimas oportunidades del mercado público.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Análisis Detallado</h5>
                        <p class="card-text">Visualiza estadísticas y tendencias para tomar mejores decisiones.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

```

### ./app/templates/about.html
```text
{% extends "base.html" %}

{% block title %}Acerca de - Mercado Público Monitor{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h2 class="card-title">Acerca de Mercado Público Monitor</h2>
        <div class="mt-4">
            <h4>Descripción</h4>
            <p>
                Mercado Público Monitor es una herramienta diseñada para facilitar el seguimiento
                de licitaciones públicas en Chile. Permite la búsqueda automatizada y el análisis
                de oportunidades de negocio en el mercado público.
            </p>
            
            <h4 class="mt-4">Características</h4>
            <ul>
                <li>Búsqueda automatizada de licitaciones</li>
                <li>Filtrado por palabras clave</li>
                <li>Análisis estadístico</li>
                <li>Interfaz intuitiva</li>
                <li>Exportación de datos</li>
            </ul>
            
            <h4 class="mt-4">Tecnologías</h4>
            <ul>
                <li>Backend: Python, FastAPI, SQLAlchemy</li>
                <li>Frontend: HTML5, Bootstrap 5, JavaScript</li>
                <li>Base de datos: SQLite</li>
            </ul>
            
            <h4 class="mt-4">Autor</h4>
            <p>
                Desarrollado por [Tu Nombre]<br>
                Versión: 1.0.0<br>
                Fecha: 2024
            </p>
        </div>
    </div>
</div>
{% endblock %}

```

### ./app/templates/base.html
```text
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mercado Público Monitor{% endblock %}</title>

    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- DataTables CSS -->
    <link href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="{{ url_for('static', path='/css/styles.css') }}" rel="stylesheet">
</head>
<body class="bg-dark text-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">MP Monitor</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Inicio</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/tenders">Licitaciones</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/chat">Chat</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/settings">Configuración</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/execute">Ejecutar</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/about">Acerca de</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <!-- DataTables -->
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <!-- Custom JS -->
    <script src="{{ url_for('static', path='/js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>

```

### ./app/templates/execute.html
```text
{% extends "base.html" %}

{% block title %}Ejecutar - Mercado Público Monitor{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h2 class="card-title">Ejecutar Búsqueda</h2>
        <form id="executeForm" class="mt-4">
            <div class="mb-3">
                <label for="daysBack" class="form-label">Días a recorrer</label>
                <input type="number" class="form-control" id="daysBack" 
                       value="30" min="1" max="90">
                <small class="text-muted">Número de días hacia atrás para buscar licitaciones</small>
            </div>
            <button type="submit" class="btn btn-primary" id="executeButton">
                Iniciar Búsqueda
            </button>
        </form>
        <div id="executeStatus" class="mt-4 d-none">
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 100%"></div>
            </div>
            <p class="text-center mt-2" id="statusMessage">Procesando búsqueda...</p>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('executeForm');
    const button = document.getElementById('executeButton');
    const status = document.getElementById('executeStatus');
    const statusMessage = document.getElementById('statusMessage');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const days = document.getElementById('daysBack').value;
        
        try {
            // Disable button and show status
            button.disabled = true;
            status.classList.remove('d-none');
            statusMessage.textContent = 'Iniciando búsqueda...';
            
            // Make API request
            const response = await fetch('/api/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ days: parseInt(days) })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                statusMessage.textContent = 'Búsqueda en proceso. Puedes continuar navegando...';
                
                // Opcional: Mostrar notificación
                if ("Notification" in window) {
                    Notification.requestPermission().then(function(permission) {
                        if (permission === "granted") {
                            new Notification("Búsqueda iniciada", {
                                body: "La búsqueda se está ejecutando en segundo plano"
                            });
                        }
                    });
                }
            } else {
                throw new Error(data.detail || 'Error al ejecutar la búsqueda');
            }
            
        } catch (error) {
            console.error('Error:', error);
            statusMessage.textContent = `Error: ${error.message}`;
            status.classList.add('alert', 'alert-danger');
        } finally {
            // Re-enable button after 3 seconds
            setTimeout(() => {
                button.disabled = false;
            }, 3000);
        }
    });
});
</script>
{% endblock %}

```

### ./app/templates/settings.html
```text
<!-- app/templates/settings.html -->
{% extends "base.html" %}

{% block content %}
<div class="card">
    <div class="card-header">
        Keywords Settings
    </div>
        
    <!-- Add new keyword form -->
    <div class="card mb-4">
        <div class="card-body">
            <h5 class="card-title">Add New Keyword</h5>
            <form id="addKeywordForm" class="row g-3">
                <div class="col-md-6">
                    <input type="text" class="form-control" id="newKeyword" required placeholder="Enter keyword">
                </div>
                <div class="col-md-4">
                    <select class="form-select" id="keywordType" required>
                        <option value="include">Include</option>
                        <option value="exclude">Exclude</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary">Add</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Keywords lists -->
    <div class="row">
        <!-- Include keywords -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-success text-white">
                    Include Keywords
                </div>
                <div class="card-body">
                    <ul id="includeKeywordsList" class="list-group">
                        <!-- Keywords will be added here dynamically -->
                    </ul>
                </div>
            </div>
        </div>

        <!-- Exclude keywords -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-danger text-white">
                    Exclude Keywords
                </div>
                <div class="card-body">
                    <ul id="excludeKeywordsList" class="list-group">
                        <!-- Keywords will be added here dynamically -->
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Edit keyword modal -->
<div class="modal fade" id="editKeywordModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Keyword</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="editKeywordForm">
                    <input type="hidden" id="editKeywordId">
                    <div class="mb-3">
                        <label for="editKeywordText" class="form-label">Keyword</label>
                        <input type="text" class="form-control" id="editKeywordText" required>
                    </div>
                    <div class="mb-3">
                        <label for="editKeywordType" class="form-label">Type</label>
                        <select class="form-select" id="editKeywordType" required>
                            <option value="include">Include</option>
                            <option value="exclude">Exclude</option>
                        </select>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="saveKeywordEdit">Save</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    loadKeywords();

    // Add keyword form submission
    document.getElementById('addKeywordForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const keyword = document.getElementById('newKeyword').value;
        const type = document.getElementById('keywordType').value;
        addKeyword(keyword, type);
    });

    // Save edit button click
    document.getElementById('saveKeywordEdit').addEventListener('click', function() {
        const id = document.getElementById('editKeywordId').value;
        const keyword = document.getElementById('editKeywordText').value;
        const type = document.getElementById('editKeywordType').value;
        updateKeyword(id, keyword, type);
    });
});

function loadKeywords() {
    fetch('/api/keywords')
        .then(response => response.json())
        .then(keywords => {
            const includeList = document.getElementById('includeKeywordsList');
            const excludeList = document.getElementById('excludeKeywordsList');
            
            includeList.innerHTML = '';
            excludeList.innerHTML = '';

            keywords.forEach(keyword => {
                const listItem = createKeywordListItem(keyword);
                if (keyword.type === 'include') {
                    includeList.appendChild(listItem);
                } else {
                    excludeList.appendChild(listItem);
                }
            });
        })
        .catch(error => console.error('Error loading keywords:', error));
}

function createKeywordListItem(keyword) {
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.innerHTML = `
        <span>${keyword.keyword}</span>
        <div>
            <button class="btn btn-sm btn-outline-primary me-2" onclick="editKeyword(${keyword.id}, '${keyword.keyword}', '${keyword.type}')">
                <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteKeyword(${keyword.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    return li;
}

function addKeyword(keyword, type) {
    fetch('/api/keywords', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword, type })
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('newKeyword').value = '';
            loadKeywords();
        }
    })
    .catch(error => console.error('Error adding keyword:', error));
}

function editKeyword(id, keyword, type) {
    document.getElementById('editKeywordId').value = id;
    document.getElementById('editKeywordText').value = keyword;
    document.getElementById('editKeywordType').value = type;
    
    new bootstrap.Modal(document.getElementById('editKeywordModal')).show();
}

function updateKeyword(id, keyword, type) {
    fetch(`/api/keywords/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword, type })
    })
    .then(response => {
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('editKeywordModal')).hide();
            loadKeywords();
        }
    })
    .catch(error => console.error('Error updating keyword:', error));
}

function deleteKeyword(id) {
    if (confirm('Are you sure you want to delete this keyword?')) {
        fetch(`/api/keywords/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                loadKeywords();
            }
        })
        .catch(error => console.error('Error deleting keyword:', error));
    }
}
</script>
{% endblock %}

```

### ./app/templates/tenders.html
```text
{% extends "base.html" %}

{% block title %}Licitaciones - Mercado Público Monitor{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h2 class="card-title">Licitaciones Encontradas</h2>
        <div class="table-responsive mt-4">
            <table id="tendersTable" class="table table-dark table-striped">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Nombre</th>
                        <th>Organismo</th>
                        <th>Estado</th>
                        <th>Monto Estimado</th>
                        <th>Fecha Cierre</th>
                        <th>Tipo</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
$(document).ready(function() {
    $('#tendersTable').DataTable({
        ajax: {
            url: '/api/tenders',
            dataSrc: ''
        },
        columns: [
            { data: 'code' },
            { data: 'name' },
            { data: 'organization' },
            { data: 'status' },
            { 
                data: 'estimated_amount',
                render: function(data) {
                    return data ? `$${data.toLocaleString()}` : 'No especificado';
                }
            },
            { 
                data: 'closing_date',
                render: function(data) {
                    return data ? new Date(data).toLocaleDateString() : 'No especificado';
                }
            },
            { data: 'tender_type' }
        ],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
        },
        order: [[5, 'desc']],
        pageLength: 200,
        dom: 'Bfrtip',
        buttons: ['copy', 'csv', 'excel', 'pdf']
    });
});
</script>
{% endblock %}

```

### ./app/templates/chat.html
```text
{% extends "base.html" %}

{% block title %}Chat - Mercado Público Monitor{% endblock %}

{% block content %}
<div class="card">
    <div class="card-body">
        <h2 class="card-title">Chat</h2>
        <p class="card-text">
            Esta funcionalidad estará disponible próximamente.
        </p>
    </div>
</div>
{% endblock %}

```

### ./src/__init__.py
```python

```

### ./src/database/__init__.py
```python

```

### ./src/database/repository.py
```python
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime
from src.models.tender import Tender
from src.models.keywords import Keyword, KeywordType
from src.utils.logger import setup_logger

class TenderRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(__name__)

    def create_tender(self, tender: Tender) -> Tender:
        """
        Create a new tender in the database
        
        Args:
            tender (Tender): Tender object to create
            
        Returns:
            Tender: Created tender object
        """
        try:
            tender.created_at = datetime.utcnow()
            tender.updated_at = datetime.utcnow()
            
            self.logger.debug(f"Creating new tender with code: {tender.code}")
            self.db.add(tender)
            self.db.commit()
            self.db.refresh(tender)
            return tender
        except Exception as e:
            self.logger.error(f"Error creating tender {tender.code}: {str(e)}")
            self.db.rollback()
            raise

    def update_tender(self, new_tender: Tender) -> Tender:
        """
        Update an existing tender if there are changes
        
        Args:
            new_tender (Tender): Tender object with updated data
            
        Returns:
            Tender: Updated tender object
        """
        try:
            existing_tender = self.get_tender_by_code(new_tender.code)
            if not existing_tender:
                return self.create_tender(new_tender)

            # Compare relevant fields to check if update is needed
            fields_to_compare = [
                'name', 'description', 'status', 'status_code', 'estimated_amount',
                'closing_date', 'award_date', 'number_of_bidders', 'items',
                'awarded_suppliers'
            ]

            needs_update = False
            for field in fields_to_compare:
                old_value = getattr(existing_tender, field)
                new_value = getattr(new_tender, field)
                if old_value != new_value:
                    needs_update = True
                    self.logger.debug(f"Field {field} changed from {old_value} to {new_value}")
                    setattr(existing_tender, field, new_value)

            if needs_update:
                existing_tender.updated_at = datetime.utcnow()
                self.logger.info(f"Updating tender {existing_tender.code}")
                self.db.commit()
                self.db.refresh(existing_tender)
            else:
                self.logger.debug(f"No updates needed for tender {existing_tender.code}")

            return existing_tender

        except Exception as e:
            self.logger.error(f"Error updating tender {new_tender.code}: {str(e)}")
            self.db.rollback()
            raise

    def get_tender_by_code(self, code: str) -> Optional[Tender]:
        """
        Get a tender by its code
        
        Args:
            code (str): Tender code to search for
            
        Returns:
            Optional[Tender]: Found tender or None
        """
        return self.db.query(Tender).filter(Tender.code == code).first()

    def get_tenders_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Tender]:
        """
        Get all tenders within a date range
        
        Args:
            start_date (datetime): Start date of the range
            end_date (datetime): End date of the range
            
        Returns:
            List[Tender]: List of tenders within the date range
        """
        return self.db.query(Tender).filter(
            Tender.creation_date.between(start_date, end_date)
        ).all()

    def delete_tender(self, tender: Tender) -> None:
        """
        Delete a tender from the database
        
        Args:
            tender (Tender): Tender object to delete
        """
        self.db.delete(tender)
        self.db.commit()

    def get_all_tenders(self) -> List[Tender]:
        """
        Get all tenders from the database
        
        Returns:
            List[Tender]: List of all tenders
        """
        try:
            return self.db.query(Tender).order_by(Tender.created_at.desc()).all()
        except Exception as e:
            self.logger.error(f"Error getting all tenders: {str(e)}")
            raise

    def get_tenders_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Tender]:
        """
        Get tenders with filters
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            search (str, optional): Search term for name or description
            status (str, optional): Filter by status
            start_date (datetime, optional): Filter by start date
            end_date (datetime, optional): Filter by end date
            
        Returns:
            List[Tender]: List of filtered tenders
        """
        try:
            query = self.db.query(Tender)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Tender.name.ilike(search_term),
                        Tender.description.ilike(search_term)
                    )
                )

            if status:
                query = query.filter(Tender.status == status)

            if start_date:
                query = query.filter(Tender.creation_date >= start_date)

            if end_date:
                query = query.filter(Tender.creation_date <= end_date)

            return query.order_by(Tender.created_at.desc()).offset(skip).limit(limit).all()

        except Exception as e:
            self.logger.error(f"Error getting filtered tenders: {str(e)}")
            raise

class KeywordRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(__name__)

    def create_keyword(self, keyword: str, type: KeywordType) -> Keyword:
        """
        Create a new keyword
        
        Args:
            keyword (str): Keyword text
            type (KeywordType): Type of keyword (include/exclude)
            
        Returns:
            Keyword: Created keyword object
        """
        try:
            new_keyword = Keyword(keyword=keyword, type=type)
            self.db.add(new_keyword)
            self.db.commit()
            self.db.refresh(new_keyword)
            return new_keyword
        except Exception as e:
            self.logger.error(f"Error creating keyword: {str(e)}")
            self.db.rollback()
            raise

    def get_all_keywords(self) -> List[Keyword]:
        """
        Get all keywords
        
        Returns:
            List[Keyword]: List of all keywords
        """
        return self.db.query(Keyword).all()

    def get_keywords_by_type(self, type: KeywordType) -> List[Keyword]:
        """
        Get keywords by type
        
        Args:
            type (KeywordType): Type of keywords to retrieve
            
        Returns:
            List[Keyword]: List of keywords of specified type
        """
        return self.db.query(Keyword).filter(Keyword.type == type).all()

    def delete_keyword(self, keyword_id: int) -> bool:
        """
        Delete a keyword
        
        Args:
            keyword_id (int): ID of keyword to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            keyword = self.db.query(Keyword).filter(Keyword.id == keyword_id).first()
            if keyword:
                self.db.delete(keyword)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting keyword: {str(e)}")
            self.db.rollback()
            return False

    def update_keyword(self, keyword_id: int, new_keyword: str = None, 
                      new_type: KeywordType = None) -> Optional[Keyword]:
        """
        Update a keyword
        
        Args:
            keyword_id (int): ID of keyword to update
            new_keyword (str, optional): New keyword text
            new_type (KeywordType, optional): New keyword type
            
        Returns:
            Optional[Keyword]: Updated keyword object or None if not found
        """
        try:
            keyword = self.db.query(Keyword).filter(Keyword.id == keyword_id).first()
            if keyword:
                if new_keyword is not None:
                    keyword.keyword = new_keyword
                if new_type is not None:
                    keyword.type = new_type
                self.db.commit()
                self.db.refresh(keyword)
                return keyword
            return None
        except Exception as e:
            self.logger.error(f"Error updating keyword: {str(e)}")
            self.db.rollback()
            return None

    def initialize_default_keywords(self) -> None:
        """
        Initialize default keywords if the keywords table is empty
        """
        if not self.get_all_keywords():
            # Default include keywords
            default_includes = [
                "software", "analisis", "datos", "inteligencia artificial", "web",
                "aplicación", "plataforma", "digital",
                "tecnología", "informática", "computación", "desarrollo"
            ]
            
            # Default exclude keywords
            default_excludes = [
                "limpieza", "licencia", "suscripción", "mantención", "aseo", "arriendo", "equipos", "equipamiento", "exámenes", "insumos", "antenas", "datos de internet",
            ]
            
            try:
                # Add include keywords
                for keyword in default_includes:
                    self.create_keyword(keyword, KeywordType.INCLUDE)
                    
                # Add exclude keywords
                for keyword in default_excludes:
                    self.create_keyword(keyword, KeywordType.EXCLUDE)
                
                self.logger.info("Default keywords initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing default keywords: {str(e)}")
                raise

```

### ./src/database/base.py
```python
# src/database/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import make_url
from src.config.settings import DATABASE_URL
from src.utils.logger import setup_logger
import os

logger = setup_logger(__name__)

def get_engine_config():
    """
    Configure database engine based on DATABASE_URL
    
    Returns:
        tuple: (engine, kwargs) where engine is the SQLAlchemy engine and 
               kwargs are additional configuration parameters
    """
    url = make_url(DATABASE_URL)
    
    if url.drivername == 'postgresql':
        # PostgreSQL configuration
        return create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False
        )
    elif 'sqlite' in url.drivername:
        # SQLite configuration
        # Ensure the directory exists
        db_path = url.database
        if db_path != ':memory:':
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        raise ValueError(f"Unsupported database type: {url.drivername}")

try:
    # Create engine based on URL
    engine = get_engine_config()
    logger.info(f"Database engine configured for: {make_url(DATABASE_URL).drivername}")
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create base class for declarative models
    Base = declarative_base()
    
except Exception as e:
    logger.error(f"Failed to configure database: {str(e)}")
    raise

def init_db():
    """Initialize the database and create all tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_db():
    """Database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

### ./src/config/__init__.py
```python

```

### ./src/config/settings.py
```python
import os
from dotenv import load_dotenv

# If .env file exists, load environment variables from it
if os.path.exists('.env'):
    load_dotenv()

# API Configuration
API_BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
API_TICKET = os.getenv('TICKET_KEY')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

```

### ./src/utils/__init__.py
```python

```

### ./src/utils/logger.py
```python
import logging
from src.config.settings import LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger

```

### ./src/utils/safe_load.py
```python
from typing import Optional, Any
from datetime import datetime
import unicodedata

def remove_accents(text: str) -> str:
    """
    Remove accents from text
    
    Args:
        text (str): Text to process
        
    Returns:
        str: Text without accents
    """
    if not text:
        return ""
    
    try:
        # Normalize to decomposed form (separate char and accent)
        nfkd_form = unicodedata.normalize('NFKD', str(text))
        # Remove accents (non-spacing marks)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    except Exception:
        return text

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None

def safe_bool(value: Any) -> Optional[bool]:
    """Safely convert value to boolean"""
    if value is None:
        return None
    try:
        return str(value).lower() in ('1', 'true', 'yes', 'si')
    except (ValueError, AttributeError):
        return None

def safe_int(value: Any) -> Optional[int]:
    """Safely convert value to integer"""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
```

### ./src/models/keywords.py
```python
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from src.database.base import Base
import enum

class KeywordType(enum.Enum):
    """Type of keyword for filtering"""
    INCLUDE = "include"
    EXCLUDE = "exclude"

class Keyword(Base):
    """Model for storing search keywords"""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True, 
                doc="Unique identifier for the keyword")
    keyword = Column(String, nullable=False, unique=True, 
                    doc="The keyword text to search for")
    type = Column(SQLAlchemyEnum(KeywordType), nullable=False, default=KeywordType.INCLUDE,
                 doc="Type of keyword (include/exclude)")

    def __repr__(self):
        """String representation of the keyword"""
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', type={self.type.value})>"

```

### ./src/models/__init__.py
```python

```

### ./src/models/tender.py
```python
# src/models/tender.py
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.database.base import Base

from .enum import (
    AdministrativeActType,
    Currency,
    EstimationType,
    PaymentModality,
    TenderType,
    TimeUnit,
    PaymentType,
)

class Tender(Base):
    __tablename__ = "tenders"

    # Identificación y datos básicos
    code = Column(String, primary_key=True, doc="Código único de la licitación")
    name = Column(String, nullable=True, doc="Nombre de la licitación")
    description = Column(String, nullable=True, doc="Descripción detallada de la licitación")
    status = Column(String, nullable=True, doc="Estado actual de la licitación")
    status_code = Column(Integer, nullable=True, doc="Código numérico del estado")
    api_version = Column(String, nullable=True, doc="Versión de la API")

    # Clasificación y tipo
    tender_type = Column(
        SQLAlchemyEnum(TenderType), nullable=True, doc="Tipo de licitación según monto UTM"
    )
    currency = Column(SQLAlchemyEnum(Currency), nullable=True, doc="Moneda de la licitación")
    bidding_stages = Column(Integer, nullable=True, doc="Número de etapas (1 o 2)")
    bidding_stages_status = Column(Integer, nullable=True, doc="Estado de las etapas")

    # Información financiera
    estimated_amount = Column(BigInteger, nullable=True, doc="Monto estimado de la licitación")
    estimation_type = Column(
        SQLAlchemyEnum(EstimationType), nullable=True, doc="Tipo de estimación del monto"
    )
    amount_visibility = Column(Boolean, nullable=True, doc="Visibilidad del monto estimado")
    payment_modality = Column(
        SQLAlchemyEnum(PaymentModality), nullable=True, doc="Modalidad de pago"
    )
    payment_type = Column(
        SQLAlchemyEnum(PaymentType),
        nullable=True,
        doc="Tipo de pago que se realizará"
    )
    financing_source = Column(String, nullable=True, doc="Fuente de financiamiento")

    # Información de la organización compradora
    organization = Column(String, nullable=True, doc="Nombre del organismo comprador")
    organization_code = Column(String, nullable=True, doc="Código del organismo")
    organization_tax_id = Column(String, nullable=True, doc="RUT del organismo")
    buying_unit = Column(String, nullable=True, doc="Nombre de la unidad compradora")
    buying_unit_code = Column(String, nullable=True, doc="Código de la unidad compradora")
    buying_unit_address = Column(String, nullable=True, doc="Dirección de la unidad compradora")
    buying_unit_region = Column(String, nullable=True, doc="Región de la unidad compradora")
    buying_unit_commune = Column(String, nullable=True, doc="Comuna de la unidad compradora")

    # Información del usuario responsable
    user_tax_id = Column(String, nullable=True, doc="RUT del usuario responsable")
    user_code = Column(String, nullable=True, doc="Código del usuario")
    user_name = Column(String, nullable=True, doc="Nombre del usuario")
    user_position = Column(String, nullable=True, doc="Cargo del usuario")

    # Fechas importantes
    creation_date = Column(DateTime, nullable=True, doc="Fecha de creación")
    publication_date = Column(DateTime, nullable=True, doc="Fecha de publicación")
    closing_date = Column(DateTime, nullable=True, doc="Fecha de cierre")
    questions_deadline = Column(DateTime, nullable=True, doc="Fecha límite de preguntas")
    answers_publication_date = Column(
        DateTime, nullable=True, doc="Fecha de publicación de respuestas"
    )
    technical_opening_date = Column(DateTime, nullable=True, doc="Fecha de apertura técnica")
    economic_opening_date = Column(DateTime, nullable=True, doc="Fecha de apertura económica")
    award_date = Column(DateTime, nullable=True, doc="Fecha de adjudicación")
    estimated_award_date = Column(DateTime, nullable=True, doc="Fecha estimada de adjudicación")
    site_visit_date = Column(DateTime, nullable=True, doc="Fecha de visita a terreno")
    background_delivery_date = Column(
        DateTime, nullable=True, doc="Fecha de entrega de antecedentes"
    )
    physical_support_date = Column(DateTime, nullable=True, doc="Fecha de soporte físico")
    evaluation_date = Column(DateTime, nullable=True, doc="Fecha de evaluación")
    estimated_signing_date = Column(DateTime, nullable=True, doc="Fecha estimada de firma")
    user_defined_date = Column(DateTime, nullable=True, doc="Fecha definida por usuario")

    # Unidades de tiempo
    evaluation_time_unit = Column(
        SQLAlchemyEnum(TimeUnit), nullable=True, doc="Unidad de tiempo para evaluación"
    )
    contract_time_unit = Column(
        SQLAlchemyEnum(TimeUnit), nullable=True, doc="Unidad de tiempo del contrato"
    )

    # Información de contacto
    payment_responsible_name = Column(String, nullable=True, doc="Nombre del responsable de pago")
    payment_responsible_email = Column(String, nullable=True, doc="Email del responsable de pago")
    contract_responsible_name = Column(
        String, nullable=True, doc="Nombre del responsable del contrato"
    )
    contract_responsible_email = Column(
        String, nullable=True, doc="Email del responsable del contrato"
    )
    contract_responsible_phone = Column(
        String, nullable=True, doc="Teléfono del responsable del contrato"
    )

    # Información del contrato
    allows_subcontracting = Column(Boolean, nullable=True, doc="Permite subcontratación")
    contract_duration = Column(Integer, nullable=True, doc="Duración del contrato")
    contract_duration_type = Column(String, nullable=True, doc="Tipo de duración del contrato")
    is_renewable = Column(Boolean, nullable=True, doc="Es renovable")
    renewal_time_value = Column(Integer, nullable=True, doc="Valor tiempo de renovación")
    renewal_time_period = Column(String, nullable=True, doc="Período de tiempo de renovación")

    # Control y regulación
    requires_comptroller = Column(
        Boolean, nullable=True, doc="Requiere toma de razón de Contraloría"
    )
    technical_offer_publicity = Column(Integer, nullable=True, doc="Publicidad de oferta técnica")
    publicity_justification = Column(String, nullable=True, doc="Justificación de publicidad")
    hiring_prohibition = Column(String, nullable=True, doc="Prohibición de contratación")
    amount_justification = Column(String, nullable=True, doc="Justificación del monto")
    deadline_extension = Column(Integer, nullable=True, doc="Extensión de plazo")

    # Flags y estados
    is_public_bid = Column(Boolean, nullable=True, doc="Es licitación pública")
    is_informed = Column(Boolean, nullable=True, doc="Está informada")
    is_base_type = Column(Boolean, nullable=True, doc="Es tipo base")

    # Información de adjudicación
    award_type = Column(
        SQLAlchemyEnum(AdministrativeActType), nullable=True, doc="Tipo de acto administrativo"
    )
    award_document_number = Column(String, nullable=True, doc="Número de documento de adjudicación")
    award_document_date = Column(DateTime, nullable=True, doc="Fecha del documento de adjudicación")
    number_of_bidders = Column(Integer, nullable=True, doc="Número de oferentes")
    award_act_url = Column(String, nullable=True, doc="URL del acta de adjudicación")
    complaint_count = Column(Integer, nullable=True, doc="Cantidad de reclamos")

    # Datos adicionales
    items = Column("items", JSON, nullable=True, doc="Información de ítems en formato JSON")
    awarded_suppliers = Column(JSON, nullable=True, doc="Información de proveedores adjudicados")

    # Relaciones
    tender_items = relationship("TenderItem", back_populates="tender", cascade="all, delete-orphan")

    # Fechas de creación y actualización
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       doc="Date when the tender was first added to the database")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       onupdate=datetime.utcnow,
                       doc="Date when the tender was last updated in the database")


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'code': self.code,
            'name': self.name,
            'status': self.status,
            'organization': self.organization,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'estimated_amount': float(self.estimated_amount) if self.estimated_amount else None,
            'tender_type': str(self.tender_type.value) if self.tender_type else None
        }

    def get_payment_description(self) -> str:
        """Returns a human-readable payment modality description"""
        return self.payment_modality.description if self.payment_modality else "No especificado"

    def get_duration_description(self) -> str:
        """Returns a formatted duration description"""
        if self.contract_duration and self.contract_time_unit:
            return f"{self.contract_duration} {self.contract_time_unit.description}"
        return "No especificado"

    def is_high_value_tender(self) -> bool:
        """Checks if this is a high-value tender"""
        return self.tender_type in [TenderType.LQ, TenderType.LR] if self.tender_type else False

    def get_status_description(self) -> str:
        """Returns a human-readable status description"""
        status_map = {
            1: "Publicada",
            2: "Cerrada",
            3: "Desierta",
            4: "Adjudicada",
            5: "Revocada",
            6: "Suspendida",
            7: "En Evaluación",
        }
        return status_map.get(self.status_code, "Estado desconocido")

    def get_payment_type_description(self) -> str:
        """Returns a human-readable payment type description"""
        return self.payment_type.description if self.payment_type else "No especificado"

    def __repr__(self):
        """String representation of the tender"""
        return (
            f"<Tender(code={self.code}, name={self.name}, status={self.get_status_description()})>"
        )


class TenderItem(Base):
    __tablename__ = "tender_items"

    id = Column(Integer, primary_key=True)
    tender_code = Column(String, ForeignKey("tenders.code"))
    correlative = Column(String, nullable=True)
    category_code = Column(String, nullable=True)
    category_name = Column(String, nullable=True)
    product_code = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    # Relationship
    tender = relationship("Tender", back_populates="tender_items")

```

### ./src/models/enum.py
```python
# src/models/enum.py
from enum import Enum
from typing import Optional, Any

class BaseEnum(Enum):
    """Base Enum class with common functionality"""
    @classmethod
    def from_value(cls, value: Any) -> Optional['BaseEnum']:
        """
        Convert a value to enum member, returning None if invalid
        
        Args:
            value: The value to convert
            
        Returns:
            Optional[BaseEnum]: The enum member or None if not found
        """
        if value is None:
            return None
        try:
            return cls(value)
        except (ValueError, TypeError):
            return None


    @classmethod
    def get_default(cls) -> 'BaseEnum':
        """Get the default value for this enum"""
        return list(cls)[0]

class TenderType(BaseEnum):
    """Types of tenders based on UTM amounts"""
    L1 = "L1", "Licitación Pública Menor a 100 UTM"
    LE = "LE", "Licitación Pública igual o superior a 100 UTM e inferior a 1.000 UTM"
    LP = "LP", "Licitación Pública igual o superior a 1.000 UTM e inferior a 2.000 UTM"
    LQ = "LQ", "Licitación Pública igual o superior a 2.000 UTM e inferior a 5.000 UTM"
    LR = "LR", "Licitación Pública igual o superior a 5.000 UTM"
    E2 = "E2", "Licitación Privada Menor a 100 UTM"
    CO = "CO", "Licitación Privada igual o superior a 100 UTM e inferior a 1000 UTM"
    B2 = "B2", "Licitación Privada igual o superior a 1000 UTM e inferior a 2000 UTM"
    H2 = "H2", "Licitación Privada igual o superior a 2000 UTM e inferior a 5000 UTM"
    I2 = "I2", "Licitación Privada Mayor a 5000 UTM"
    LS = "LS", "Licitación Pública Servicios personales especializados"

    def __new__(cls, code: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.description = description
        return obj

class Currency(BaseEnum):
    """Available currencies"""
    CLP = "CLP", "Peso Chileno"
    CLF = "CLF", "Unidad de Fomento"
    USD = "USD", "Dólar Americano"
    UTM = "UTM", "Unidad Tributaria Mensual"
    EUR = "EUR", "Euro"

    def __new__(cls, code: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.description = description
        return obj

class EstimationType(BaseEnum):
    """Types of amount estimation"""
    AVAILABLE_BUDGET = 1, "Presupuesto Disponible"
    REFERENCE_PRICE = 2, "Precio Referencial"
    CANNOT_ESTIMATE = 3, "Monto no es posible de estimar"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class PaymentModality(BaseEnum):
    """Payment modalities"""
    DAYS_30 = 1, "Pago a 30 días"
    DAYS_30_60_90 = 2, "Pago a 30, 60 y 90 días"
    SAME_DAY = 3, "Pago al día"
    ANNUAL = 4, "Pago Anual"
    BIMONTHLY = 5, "Pago Bimensual"
    ON_DELIVERY = 6, "Pago Contra Entrega Conforme"
    MONTHLY = 7, "Pagos Mensuales"
    BY_PROGRESS = 8, "Pago Por Estado de Avance"
    QUARTERLY = 9, "Pago Trimestral"
    DAYS_60 = 10, "Pago a 60 días"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class TimeUnit(BaseEnum):
    """Time units for different durations"""
    HOURS = 1, "Horas"
    DAYS = 2, "Días"
    WEEKS = 3, "Semanas"
    MONTHS = 4, "Meses"
    YEARS = 5, "Años"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class AdministrativeActType(BaseEnum):
    """Types of administrative acts"""
    AUTHORIZATION = 1, "Autorización"
    RESOLUTION = 2, "Resolución"
    AGREEMENT = 3, "Acuerdo"
    DECREE = 4, "Decreto"
    OTHERS = 5, "Otros"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

class PaymentType(BaseEnum):
    """Types of payment"""
    CASH = 1, "Pago en efectivo"
    CREDIT = 2, "Pago con crédito"
    TRANSFER = 3, "Transferencia bancaria"
    CHECK = 4, "Cheque"
    ELECTRONIC = 5, "Pago electrónico"
    OTHER = 6, "Otro tipo de pago"

    def __new__(cls, value: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

```

### ./src/api/public_market_api.py
```python
from datetime import date, timedelta
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.settings import API_BASE_URL, API_TICKET
from src.models.enum import (
    AdministrativeActType,
    Currency,
    EstimationType,
    PaymentModality,
    TenderType,
    TimeUnit,
    PaymentType,
)
from src.models.tender import Tender
from src.utils.logger import setup_logger
from src.utils.safe_load import parse_date, safe_bool, safe_float, safe_int, remove_accents


class PublicMarketAPI:
    """Class to interact with the Public Market API"""

    def __init__(self):
        """Initialize API with configuration"""
        self.ticket = API_TICKET
        self.base_url = API_BASE_URL
        self.logger = setup_logger(__name__)

        # Configure session with retry strategy
        self.session = self._configure_session()

    def _configure_session(self) -> requests.Session:
        """
        Configure requests session with retry strategy

        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """
        Makes an API request with error handling and detailed logging

        Args:
            params: Dictionary with request parameters

        Returns:
            Optional[Dict]: JSON response from the API or None if request fails

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            self.logger.debug(f"Making request with parameters: {params}")
            response = self.session.get(self.base_url, params=params, timeout=(5, 30))
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"Number of tenders in response: {data.get('Cantidad', 0)}")
            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            return None

    def get_tender_details(self, code: str) -> Optional[Dict]:
        """
        Get detailed information for a specific tender

        Args:
            code: Tender code to search

        Returns:
            Optional[Dict]: Detailed tender information or None if not found
        """
        if not code:
            return None

        params = {"ticket": self.ticket, "codigo": code}

        try:
            self.logger.debug(f"Getting details for tender {code}")
            data = self._make_request(params)

            if not data or "Listado" not in data or not data["Listado"]:
                self.logger.warning(f"No valid details found for tender {code}")
                return None

            tender_data = data["Listado"][0]
            if not isinstance(tender_data, dict):
                self.logger.warning(f"Invalid data format for tender {code}")
                return None

            return tender_data

        except Exception as e:
            self.logger.error(f"Error getting tender details for {code}: {str(e)}")
            return None

    def search_tenders(self, include_keywords: List[str], exclude_keywords: List[str] = None, 
                    days_back: int = 30) -> List[Tender]:
        """
        Searches for tenders containing specified keywords
        
        Args:
            include_keywords: List of keywords to search for
            exclude_keywords: List of keywords to exclude (optional)
            days_back: Number of days to look back
            
        Returns:
            List[Tender]: List of found tenders
        """
        exclude_keywords = exclude_keywords or []
        found_tenders = []
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        self.logger.info(f"Searching tenders from {start_date} to {end_date}")
        self.logger.info(f"Include keywords: {include_keywords}")
        self.logger.info(f"Exclude keywords: {exclude_keywords}")

        current_date = start_date
        while current_date <= end_date:
            try:
                params = {
                    "ticket": self.ticket,
                    "fecha": current_date.strftime("%d%m%Y"),
                    "codigo": None,
                }

                data = self._make_request(params)
                if not data:
                    current_date += timedelta(days=1)
                    continue

                if "Listado" not in data:
                    self.logger.warning(f"No listing found for date {current_date}")
                    current_date += timedelta(days=1)
                    continue

                tenders = data["Listado"]
                self.logger.info(f"Tenders found for {current_date}: {len(tenders)}")

                for tender_data in tenders:
                    try:
                        if self._matches_keyword_criteria(tender_data, include_keywords, exclude_keywords):
                            tender_code = tender_data.get("CodigoExterno")
                            if not tender_code:
                                continue

                            detailed_data = self.get_tender_details(tender_code)
                            if not detailed_data:
                                continue

                            tender = self._parse_tender(detailed_data)
                            if tender:
                                found_tenders.append(tender)
                                self.logger.debug(
                                    f"Tender {tender.code} matched keywords and was added"
                                )
                    except Exception as e:
                        self.logger.error(f"Error processing tender: {str(e)}")
                        continue

            except Exception as e:
                self.logger.error(f"Error processing date {current_date}: {str(e)}")

            current_date += timedelta(days=1)

        self.logger.info(f"Process completed. Total found: {len(found_tenders)}")
        return found_tenders

    def _contains_keywords(self, tender: Dict, keywords: List[str]) -> bool:
        """
        Check if tender contains any of the keywords

        Args:
            tender: Tender data dictionary
            keywords: List of keywords to search

        Returns:
            bool: True if any keyword is found
        """
        if not tender or not keywords:
            return False

        search_text = (f"{tender.get('Nombre', '')} " f"{tender.get('Descripcion', '')}").lower()

        return any(keyword.lower() in search_text for keyword in keywords)

    def _parse_tender(self, tender_data: Dict) -> Optional[Tender]:
        """
        Parse tender data into Tender object

        Args:
            tender_data: Raw tender data from API

        Returns:
            Optional[Tender]: Parsed tender object or None if parsing fails
        """
        if not tender_data or not isinstance(tender_data, dict):
            self.logger.warning("Invalid or empty tender data received")
            return None

        try:
            # Get nested dictionaries with safe defaults
            comprador = tender_data.get("Comprador") or {}
            fechas = tender_data.get("Fechas") or {}
            adjudicacion = tender_data.get("Adjudicacion") or {}
            items_data = tender_data.get("Items") or {}

            # Verificar código obligatorio
            code = tender_data.get("CodigoExterno")
            if not code:
                self.logger.warning("Tender data missing required code")
                return None

            # Parse items and awarded suppliers
            try:
                items = self._parse_items(items_data)
            except Exception as e:
                self.logger.warning(f"Error parsing items: {str(e)}")
                items = None

            try:
                awarded_suppliers = self._parse_awarded_suppliers(tender_data)
            except Exception as e:
                self.logger.warning(f"Error parsing awarded suppliers: {str(e)}")
                awarded_suppliers = None

            return Tender(
                # Identificación y datos básicos
                code=code,
                name=tender_data.get("Nombre"),
                description=tender_data.get("Descripcion"),
                status=tender_data.get("Estado"),
                status_code=safe_int(tender_data.get("CodigoEstado")),
                api_version=tender_data.get("Version"),
                # Clasificación y tipo
                tender_type=TenderType.from_value(tender_data.get("Tipo")),
                currency=Currency.from_value(tender_data.get("Moneda")),
                bidding_stages=safe_int(tender_data.get("Etapas")),
                bidding_stages_status=safe_int(tender_data.get("EstadoEtapas")),
                # Información financiera
                estimated_amount=safe_float(tender_data.get("MontoEstimado")),
                estimation_type=EstimationType.from_value(tender_data.get("Estimacion")),
                amount_visibility=safe_bool(tender_data.get("VisibilidadMonto")),
                payment_modality=PaymentModality.from_value(tender_data.get("Modalidad")),
                payment_type=PaymentType.from_value(tender_data.get("TipoPago")),
                financing_source=str(tender_data.get('FuenteFinanciamiento')) if tender_data.get('FuenteFinanciamiento') else None,
                # Información de la organización
                organization=comprador.get("NombreOrganismo"),
                organization_code=comprador.get("CodigoOrganismo"),
                organization_tax_id=comprador.get("RutUnidad"),
                buying_unit=comprador.get("NombreUnidad"),
                buying_unit_code=comprador.get("CodigoUnidad"),
                buying_unit_address=comprador.get("DireccionUnidad"),
                buying_unit_region=comprador.get("RegionUnidad"),
                buying_unit_commune=comprador.get("ComunaUnidad"),
                # Información del usuario
                user_tax_id=comprador.get("RutUsuario"),
                user_code=comprador.get("CodigoUsuario"),
                user_name=comprador.get("NombreUsuario"),
                user_position=comprador.get("CargoUsuario"),
                # Fechas
                creation_date=parse_date(fechas.get("FechaCreacion")),
                publication_date=parse_date(fechas.get("FechaPublicacion")),
                closing_date=parse_date(fechas.get("FechaCierre")),
                questions_deadline=parse_date(fechas.get("FechaFinal")),
                answers_publication_date=parse_date(fechas.get("FechaPubRespuestas")),
                technical_opening_date=parse_date(fechas.get("FechaActoAperturaTecnica")),
                economic_opening_date=parse_date(fechas.get("FechaActoAperturaEconomica")),
                award_date=parse_date(fechas.get("FechaAdjudicacion")),
                estimated_award_date=parse_date(fechas.get("FechaEstimadaAdjudicacion")),
                site_visit_date=parse_date(fechas.get("FechaVisitaTerreno")),
                background_delivery_date=parse_date(fechas.get("FechaEntregaAntecedentes")),
                physical_support_date=parse_date(fechas.get("FechaSoporteFisico")),
                evaluation_date=parse_date(fechas.get("FechaTiempoEvaluacion")),
                estimated_signing_date=parse_date(fechas.get("FechaEstimadaFirma")),
                user_defined_date=parse_date(fechas.get("FechasUsuario")),
                # Unidades de tiempo
                evaluation_time_unit=TimeUnit.from_value(tender_data.get("UnidadTiempo")),
                contract_time_unit=TimeUnit.from_value(
                    tender_data.get("UnidadTiempoContratoLicitacion")
                ),
                # Información de contacto
                payment_responsible_name=tender_data.get("NombreResponsablePago"),
                payment_responsible_email=tender_data.get("EmailResponsablePago"),
                contract_responsible_name=tender_data.get("NombreResponsableContrato"),
                contract_responsible_email=tender_data.get("EmailResponsableContrato"),
                contract_responsible_phone=tender_data.get("FonoResponsableContrato"),
                # Información del contrato
                allows_subcontracting=safe_bool(tender_data.get("SubContratacion")),
                contract_duration=safe_int(tender_data.get("TiempoDuracionContrato")),
                contract_duration_type=tender_data.get("TipoDuracionContrato"),
                is_renewable=safe_bool(tender_data.get("EsRenovable")),
                renewal_time_value=safe_int(tender_data.get("ValorTiempoRenovacion")),
                renewal_time_period=tender_data.get("PeriodoTiempoRenovacion"),
                # Control y regulación
                requires_comptroller=safe_bool(tender_data.get("TomaRazon")),
                technical_offer_publicity=safe_int(tender_data.get("EstadoPublicidadOfertas")),
                publicity_justification=tender_data.get("JustificacionPublicidad"),
                hiring_prohibition=tender_data.get("ProhibicionContratacion"),
                amount_justification=tender_data.get("JustificacionMontoEstimado"),
                deadline_extension=safe_int(tender_data.get("ExtensionPlazo")),
                # Flags y estados
                is_public_bid=safe_bool(tender_data.get("TipoConvocatoria")),
                is_informed=safe_bool(tender_data.get("Informada")),
                is_base_type=safe_bool(tender_data.get("EsBaseTipo")),
                # Información de adjudicación
                award_type=AdministrativeActType.from_value(adjudicacion.get("Tipo")),
                award_document_number=adjudicacion.get("Numero"),
                award_document_date=parse_date(adjudicacion.get("Fecha")),
                number_of_bidders=safe_int(adjudicacion.get("NumeroOferentes")),
                award_act_url=adjudicacion.get("UrlActa"),
                complaint_count=safe_int(tender_data.get("CantidadReclamos")),
                # Datos adicionales
                items=items,
                awarded_suppliers=awarded_suppliers,
            )

        except Exception as e:
            self.logger.error(f"Error parsing tender details: {str(e)}")
            return None

    def _parse_items(self, items_data: Dict) -> List[Dict]:
        """
        Parse items data into a structured format

        Args:
            items_data: Raw items data from API

        Returns:
            List[Dict]: List of parsed items
        """
        items = []

        # Return empty list if items_data is None
        if not items_data:
            return items

        # Get listado with empty list as default
        listado = items_data.get("Listado", []) or []

        for item in listado:
            if not isinstance(item, dict):
                continue

            parsed_item = {
                "correlative": item.get("Correlativo"),
                "category_code": item.get("CodigoCategoria"),
                "category_name": item.get("Categoria"),
                "product_code": item.get("CodigoProducto"),
                "product_name": item.get("NombreProducto"),
                "description": item.get("Descripcion"),
                "quantity": safe_float(item.get("Cantidad")),
                "unit": item.get("UnidadMedida"),
                "tender_status_code": safe_int(item.get("CodigoEstadoLicitacion")),
            }

            # Only add award information if it exists
            adjudicacion = item.get("Adjudicacion")
            if isinstance(adjudicacion, dict):
                parsed_item["award"] = {
                    "supplier_tax_id": adjudicacion.get("RutProveedor"),
                    "supplier_name": adjudicacion.get("NombreProveedor"),
                    "awarded_quantity": safe_float(adjudicacion.get("CantidadAdjudicada")),
                    "unit_price": safe_float(adjudicacion.get("MontoUnitario")),
                }

            items.append(parsed_item)

        return items

    def _parse_awarded_suppliers(self, tender_data: Dict) -> List[Dict]:
        """
        Parse awarded suppliers data

        Args:
            tender_data: Raw tender data from API

        Returns:
            List[Dict]: List of awarded suppliers
        """
        awarded_suppliers = []

        # Return empty list if tender_data is None
        if not tender_data:
            return awarded_suppliers

        # Get items data safely
        items_data = tender_data.get("Items", {})
        if not items_data:
            return awarded_suppliers

        # Get listado with empty list as default
        items = items_data.get("Listado", []) or []

        for item in items:
            if not isinstance(item, dict):
                continue

            adjudicacion = item.get("Adjudicacion")
            if not isinstance(adjudicacion, dict):
                continue

            supplier = {
                "tax_id": adjudicacion.get("RutProveedor"),
                "name": adjudicacion.get("NombreProveedor"),
                "item_correlative": item.get("Correlativo"),
                "awarded_quantity": safe_float(adjudicacion.get("CantidadAdjudicada")),
                "unit_price": safe_float(adjudicacion.get("MontoUnitario")),
            }

            # Only add if we have at least tax_id or name
            if supplier["tax_id"] or supplier["name"]:
                if supplier not in awarded_suppliers:
                    awarded_suppliers.append(supplier)

        return awarded_suppliers

    def _matches_keyword_criteria(self, tender: Dict, include_keywords: List[str], 
                                exclude_keywords: List[str]) -> bool:
        """
        Check if tender matches keyword criteria
        
        Args:
            tender: Tender data dictionary
            include_keywords: List of keywords that should be included
            exclude_keywords: List of keywords that should be excluded
            
        Returns:
            bool: True if tender matches criteria
        """
        if not tender:
            return False

        # Create normalized search text without accents
        search_text = remove_accents(
            f"{tender.get('Nombre', '')} {tender.get('Descripcion', '')}"
        ).lower()

        # Normalize keywords
        normalized_exclude = [remove_accents(keyword).lower() for keyword in exclude_keywords]
        normalized_include = [remove_accents(keyword).lower() for keyword in include_keywords]

        # Check if any exclude keyword is present
        if any(keyword in search_text for keyword in normalized_exclude):
            self.logger.debug(f"Tender excluded due to matching exclude keyword")
            return False

        # If no include keywords, accept all non-excluded
        if not normalized_include:
            return True

        # Check if any include keyword is present
        matches = any(keyword in search_text for keyword in normalized_include)
        if matches:
            self.logger.debug(f"Tender matched include keyword")
        
        return matches

```

### ./src/api/__init__.py
```python

```

Crea un archivo Docker Compose con buenas prácticas para desplegarlo en Coolify. Razona paso por paso. Las variables de entorno deben ser configurables.