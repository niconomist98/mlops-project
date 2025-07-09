from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class SentimentClassificationRequest(BaseModel):
    created_at: datetime = Field(..., description="Datetime when the message was created")
    text: str = Field(..., min_length=1, description="Text message to classify")

class PredictionResponse(BaseModel):
    predicted_label: float = Field(..., description="Predicted sentiment score or class probability")
    features_importance: Dict[str, float] = Field(..., description="Importance of each feature used in prediction")
    prediction_time: str = Field(..., description="Timestamp when the prediction was made")
