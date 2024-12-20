from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router

app = FastAPI(title="Mercado Público Monitor")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(api_router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service status
    """
    try:
        health_status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "Mercado Público Monitor",
            "version": "1.0.0"
        }
        return JSONResponse(
            status_code=200,
            content=health_status
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

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
