# src/features/engineer.py
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
from sklearn.preprocessing import LabelEncoder

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('feature-engineering')

def create_features(df):
    """Create new features from existing data."""
    logger.info("Creating new features")
    
    # Make a copy to avoid modifying the original dataframe
    df= df.copy()
    
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

    cols_to_drop = ['tweet_id', 'author_id', 'created_at', 
                'text', 'response_tweet_id', 'in_response_to_tweet_id', 'tweet_date',
               'inbound']
    label_encoder = LabelEncoder()
    df['sentiment'] = label_encoder.fit_transform(df['sentiment'])
    return df

def create_preprocessor():
    """Create a preprocessing pipeline."""
    logger.info("Creating preprocessor pipeline")
    
    # Define feature groups
    categorical_features = ['tweet_year', 'tweet_month','tweet_day', 'tweet_weekday',	'tweet_hour' ,'tweet_quarter']
    numerical_features = ['text_length','word_count']
    
    # Preprocessing for numerical features
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean'))
    ])
    
    # Preprocessing for categorical features
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Combine preprocessors in a column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    return preprocessor

def run_feature_engineering(input_file, output_file, preprocessor_file):
    """Full feature engineering pipeline."""
    # Load cleaned data
    logger.info(f"Loading data from {input_file}")
    df = pd.read_csv(input_file)
    
    # Create features
    df_featured = create_features(df)
    logger.info(f"Created featured dataset with shape: {df_featured.shape}")
    
    # Create and fit the preprocessor
    preprocessor = create_preprocessor()
    X = df_featured.drop(columns=['sentiment'], errors='ignore')  # Features only
    y = df_featured['sentiment'] if 'sentiment' in df_featured.columns else None  # Target column (if available)
    X_transformed = preprocessor.fit_transform(X)
    logger.info("Fitted the preprocessor and transformed the features")
    
    # Save the preprocessor
    joblib.dump(preprocessor, preprocessor_file)
    logger.info(f"Saved preprocessor to {preprocessor_file}")
    
    # Save fully preprocessed data
   # Convert sparse matrix to dense (if necessary)
    if hasattr(X_transformed, "toarray"):
        X_dense = X_transformed.toarray()
    else:
        X_dense = X_transformed
    
    # Get feature names from the column transformer
    cat_features = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(preprocessor.transformers_[1][2])
    num_features = preprocessor.transformers_[0][2]
    feature_names = list(num_features) + list(cat_features)
    
    # Create DataFrame with proper column names
    df_transformed = pd.DataFrame(X_dense, columns=feature_names)
    
    # Add target column
    if y is not None:
        df_transformed['sentiment'] = y.values
    


    df_transformed.to_csv(output_file, index=False)
    logger.info(f"Saved fully preprocessed data to {output_file}")
    
    return df_transformed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Feature engineering for housing data.')
    parser.add_argument('--input', required=True, help='Path to cleaned CSV file')
    parser.add_argument('--output', required=True, help='Path for output CSV file (engineered features)')
    parser.add_argument('--preprocessor', required=True, help='Path for saving the preprocessor')
    
    args = parser.parse_args()
    
    run_feature_engineering(args.input, args.output, args.preprocessor)
