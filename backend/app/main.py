from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_agents, routes_workflows, routes_health, book_routes
from app.db.database import init_db
from app.utils.logger import logger
# from app.mcp.server import mcp

app = FastAPI(title="Book Writer AI")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_agents.router, prefix="/agents", tags=["Agents"])
app.include_router(routes_workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(book_routes.router, prefix="/api", tags=["Books"])

# -----------------------------
# MCP Integration (Auto-wraps OpenAPI)
# -----------------------------

mcp = FastApiMCP(app)
mcp.mount()

# -----------------------------
# Startup
# -----------------------------

@app.on_event('startup')
async def startup_event():
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.exception("DB init failed: %s", e)

@app.get('/')
async def root():
    return {'message': 'Book Writer AI backend is running'}