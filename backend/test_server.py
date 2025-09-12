"""
테스트용 간단한 FastAPI 서버
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Stock Analyzer Test")

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "Stock Analyzer API"}

@app.get("/health")
async def health():
    return HealthResponse(status="ok", message="Service is running")

@app.get("/api/v1/test")
async def test():
    return {"data": "API is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)