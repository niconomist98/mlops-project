# src/data/processor.py
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from textblob import TextBlob

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data-processor')

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


def load_data(file_path):
    """Load data from a CSV file."""
    logger.info(f"Loading data from {file_path}")
    return pd.read_csv(file_path)

def clean_data(df):
    """Clean the dataset by handling missing values and outliers."""
    logger.info("Cleaning dataset")
    
    # Make a copy to avoid modifying the original dataframe
    df_cleaned = df.copy()
    #1.
    df_cleaned = df[df['inbound'] == True].copy()

    #2.
    df_cleaned = df_cleaned[df_cleaned['text'].str.contains("AppleSupport")]

    #3.
    df_cleaned['created_at'] = pd.to_datetime(df_cleaned['created_at'], errors='coerce')

    #4. 
    df_cleaned = df_cleaned[df_cleaned['created_at'].notna()]

    #5.
    df_cleaned = df_cleaned[df_cleaned['text'].notna()]
    df_cleaned = df_cleaned[df_cleaned['text'].str.strip() != '']

    #6.
    df_cleaned['text'] = df_cleaned['text'].str.lower().str.strip()

    df_cleaned['tweet_id'] = df_cleaned['tweet_id'].astype(str)
    df_cleaned['author_id'] = df_cleaned['author_id'].astype(str)

    df_cleaned['response_tweet_id'] = df_cleaned['response_tweet_id'].fillna('').astype(str)
    df_cleaned['in_response_to_tweet_id'] = df_cleaned['in_response_to_tweet_id'].fillna('').astype(str)

    df_cleaned['sentiment'] = df_cleaned['text'].apply(get_sentiment)

    #filtramos unicamente mensajes iniciales enviados para evaluar el sentimiento de los 
    #mensajes que inician interacciones
    #con el objetivo de enfocar mejor la atención de la operacion
    
    df_cleaned = df_cleaned[df_cleaned['in_response_to_tweet_id'].isna() |      (df_cleaned['in_response_to_tweet_id'].str.strip() == '')]
    #  Reiniciar el índice del DataFrame después de los filtros
    
    df_cleaned = df_cleaned.reset_index(drop=True)
    
    return df_cleaned

def process_data(input_file, output_file):
    """Full data processing pipeline."""
    # Create output directory if it doesn't exist
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data(input_file)
    logger.info(f"Loaded data with shape: {df.shape}")
    
    # Clean data
    df_cleaned = clean_data(df)
    
    # Save processed data
    df_cleaned.to_csv(output_file, index=False)
    logger.info(f"Saved processed data to {output_file}")
    
    return df_cleaned

if __name__ == "__main__":
    # Example usage
    process_data(
        input_file="data/raw/twcs.csv", 
        output_file="data/processed/twitter_messages_processed_v1.csv"
    )
