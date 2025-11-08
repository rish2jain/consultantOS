"""
Main entry point for ConsultantOS API
"""
import uvicorn
from consultantos.api.main import app

if __name__ == "__main__":
    uvicorn.run(
        "consultantos.api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )

