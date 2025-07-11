import joblib
import pandas as pd
from datetime import datetime
from schemas import SentimentClassificationRequest, PredictionResponse

# Load model and preprocessor
MODEL_PATH = "models/trained/sentiment_classification_model.pkl"
PREPROCESSOR_PATH = "models/trained/preprocessor.pkl"

try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model or preprocessor: {str(e)}")

def tweet_classificator(request: SentimentClassificationRequest) -> PredictionResponse:
    """

    """
    # Prepare input data
    df = pd.DataFrame([request.dict()])
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    # Extract date-based features
    df['tweet_date'] = df['created_at'].dt.date
    df['tweet_year'] = df['created_at'].dt.year
    df['tweet_month'] = df['created_at'].dt.month
    df['tweet_day'] = df['created_at'].dt.day
    df['tweet_weekday'] = df['created_at'].dt.weekday  # Monday=0, Sunday=6
    df['tweet_hour'] = df['created_at'].dt.hour
    df['tweet_quarter'] = df['created_at'].dt.quarter
    # Length of tweet text in characters
    df['text_length'] = df['text'].str.len()

    # Number of words in tweet text
    df['word_count'] = df['text'].str.split().apply(len)

    # Preprocess input data
    processed_features = preprocessor.transform(df)

    # Make prediction
    predicted_label = model.predict(processed_features)[0]

    return PredictionResponse(
        predicted_label=predicted_label,
        features_importance={},
        prediction_time=datetime.now().isoformat()
    )


def batch_predict(requests: list[SentimentClassificationRequest]) -> list[float]:
    """
    Perform batch predictions.
    """
    df = pd.DataFrame([requests.dict()])
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    # Extract date-based features
    df['tweet_date'] = df['created_at'].dt.date
    df['tweet_year'] = df['created_at'].dt.year
    df['tweet_month'] = df['created_at'].dt.month
    df['tweet_day'] = df['created_at'].dt.day
    df['tweet_weekday'] = df['created_at'].dt.weekday  # Monday=0, Sunday=6
    df['tweet_hour'] = df['created_at'].dt.hour
    df['tweet_quarter'] = df['created_at'].dt.quarter
    # Length of tweet text in characters
    df['text_length'] = df['text'].str.len()

    # Number of words in tweet text
    df['word_count'] = df['text'].str.split().apply(len)


    # Preprocess input data
    processed_features = preprocessor.transform(df)

    # Make predictions
    predictions = model.predict(processed_features)
    return predictions.tolist()