from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer



if __name__ == "__main__":
    # 1. Ingestion
    print("--- Starting Ingestion ---")
    # Replace with your API KEY and a Sample Video ID
    API_KEY = "AIzaSyBS57fQDroS9l3BfOOSjaZsntkb7h-6FAI"
    VIDEO_ID = "ReZMjIoMBwY" 
    
    ingestion = DataIngestion(API_KEY)
    raw_data_path = ingestion.fetch_comments(VIDEO_ID, max_results=None)
    print(f"Data at: {raw_data_path}")

    # 2. Transformation
    print("--- Starting Transformation ---")
    transform = DataTransformation()
    X_train, y_train, X_test, y_test, preprocessor_path = transform.initiate_data_transformation(raw_data_path)
    
    import numpy as np
    total_samples = len(y_train) + len(y_test)
    positive_count = np.sum(y_train) + np.sum(y_test)
    negative_count = total_samples - positive_count
    print(f"Total Comments Analyzed: {total_samples}")
    print(f"Positive Sentiment: {positive_count} ({positive_count/total_samples:.2%})")
    print(f"Negative Sentiment: {negative_count} ({negative_count/total_samples:.2%})")
    
    print("Data Transformed.")

    # 3. Training
    print("--- Starting Training ---")
    trainer = ModelTrainer()
    score = trainer.start_training(X_train, y_train, X_test, y_test)