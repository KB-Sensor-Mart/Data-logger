import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.routes import app as core_app  # Import the router from routes.py

app = FastAPI()


# CORS Middleware for allowing external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including all routes from the routes.py file
app.include_router(core_app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)