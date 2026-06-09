from fastapi import FastAPI

from backend.app.routers.chat import router as chat_router

app = FastAPI(
    title="AI Sales & Support Assistant",
    description="AI-powered sales and customer support assistant",
    version="1.0.0"
)

# Register application routers
app.include_router(chat_router)


@app.get('/')
def root():
    """
    Root endpoint used to verify that the API is running.
    """
    
    return {
        "message": "AI Sales & Support Assistant API is running"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }