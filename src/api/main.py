from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from inference import tweet_classificator,batch_predict
from schemas import SentimentClassificationRequest, PredictionResponse

# Initialize FastAPI app with metadata
app = FastAPI(
    title="tweet classification API",
    description=(
    ),
    version="1.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "healthy", "model_loaded": True}

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: SentimentClassificationRequest):
    return tweet_classificator(request)
# Batch prediction endpoint
@app.post("/batch-predict", response_model=list)
async def batch_predict_endpoint(requests: list[SentimentClassificationRequest]):
    return batch_predict(requests)