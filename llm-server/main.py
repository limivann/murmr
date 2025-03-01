from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import json
from biomistral_inference import inference

async def lifespan(app: FastAPI):
  yield
  
app = FastAPI(lifespan=lifespan)
app.add_middleware(
  CORSMiddleware, 
  allow_credentials=True, 
  allow_origins=["*"], 
  allow_methods=["*"], 
  allow_headers=["*"]
)

class HealthData(BaseModel):
    health_data: str

@app.post("/med-summarizer")
def med_summarizer(request: HealthData):
    data= json.loads(request.health_data)
    response = inference(data)
    print("Got response")
    print(response)
    return {"analysis": response}

@app.get("/")
def root():
  return {"message": "Hello World"}

if __name__ == "__main__":
  uvicorn.run(
    app="main:app", 
    host="0.0.0.0", 
    port=8789, 
    reload=True
  )