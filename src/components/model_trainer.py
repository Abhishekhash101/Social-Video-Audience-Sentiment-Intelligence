import os
import sys
import mlflow
import mlflow.sklearn
from dataclasses import dataclass
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from lightgbm import LGBMClassifier

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def eval_metrics(self, actual, pred):
        accuracy = accuracy_score(actual, pred)
        precision = precision_score(actual, pred)
        recall = recall_score(actual, pred)
        f1 = f1_score(actual, pred)
        return accuracy, precision, recall, f1

    def initiate_model_training(self, train_array, test_array):
        try:
            logging.info("Split training and test input data")
            
            
            X_train, y_train, X_test, y_test = train_array, test_array[0], test_array[1], test_array[2] 
            pass 

        except Exception as e:
            raise CustomException(e, sys)

    # REVISED method signature to match previous step's output
    def start_training(self, X_train, y_train, X_test, y_test):
        try:
            logging.info("Starting Model Training")
            
            # 1. Define the Model
            model = LGBMClassifier(n_estimators=100, learning_rate=0.05)

            # 2. MLflow Tracking
            # This creates a local "mlruns" folder to store your experiment data
            mlflow.set_experiment("YouTube_Sentiment_Analysis")

            with mlflow.start_run():
                logging.info("Training LightGBM Model...")
                model.fit(X_train, y_train)

                logging.info("Predicting on Test Data...")
                y_pred = model.predict(X_test)

                # 3. Calculate Metrics
                accuracy, precision, recall, f1 = self.eval_metrics(y_test, y_pred)
                
                logging.info(f"Model Metrics -> Accuracy: {accuracy}, F1: {f1}")

                # 4. Log params and metrics to MLflow
                mlflow.log_param("model_type", "LightGBM")
                mlflow.log_param("n_estimators", 100)
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.log_metric("f1_score", f1)

                # 5. Log the Model itself
                mlflow.sklearn.log_model(model, "model")

                # 6. Save Model Locally (for the Flask App to use)
                save_object(
                    file_path=self.model_trainer_config.trained_model_file_path,
                    obj=model
                )

            logging.info(f"Model saved at {self.model_trainer_config.trained_model_file_path}")
            
            return accuracy

        except Exception as e:
            raise CustomException(e, sys)