from fastapi import FastAPI
from api.router import router as api_router
from db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI(title="Shop API")

# Include the API router
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the Shop API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
