from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import requests

app = FastAPI()

API_KEY = "12345"
API_KEY_NAME = "X-API-Key"

# Define a Pydantic model for the request body
class Request(BaseModel):
    prompt: str
    model: str
    stream: bool

@app.post("/generate")
async def generate(request: Request, api_key: str = Depends(APIKeyHeader(name=API_KEY_NAME))):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    url = "http://localhost:11434/api/generate" # default ollama url 
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": request.stream
    }
    headers = {
        "X-API-Key": api_key
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
