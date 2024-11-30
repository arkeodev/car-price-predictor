import os
import json
import mlflow
import pandas as pd
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any
import time
from pathlib import Path
import boto3
from botocore.client import Config
import warnings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class CarPricePredictor:
    """
    A class that handles real-time car price predictions using ML model and Kafka streaming.
    
    Key components:
    - MLflow for model management
    - Kafka for streaming data
    - MinIO for artifact storage
    - Scikit-learn for data preprocessing
    """
    
    def __init__(self):
        """Initialize empty attributes that will be set up later"""
        self.model = None          # ML model for predictions
        self.label_encoders = None # For converting categorical variables
        self.scaler = None         # For scaling numerical variables
        self.consumer = None       # Kafka consumer
        self.producer = None       # Kafka producer

    def setup_minio(self):
        """
        Configure MinIO (S3-compatible storage) credentials.
        MinIO is used to store ML artifacts.
        """
        os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'
        os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000'
        
        boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='minio',
            aws_secret_access_key='minio123',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        logger.info("MinIO credentials configured")

    def load_model_and_artifacts(self) -> None:
        """
        Load all necessary components for prediction:
        1. Label encoders for categorical variables
        2. Scaler for numerical variables
        3. ML model from MLflow
        
        Implements retry logic for MLflow connection
        """
        try:
            logger.info("Loading model and artifacts...")
            
            self.setup_minio()
            
            current_dir = Path(__file__).parent
            
            encoder_path = current_dir / 'label_encoders.pkl'
            with open(encoder_path, "rb") as f:
                self.label_encoders = pickle.load(f)
            logger.info("Loaded label encoders")
            
            scaler_path = current_dir / 'scaler.pkl'
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            logger.info("Loaded scaler")
            
            # Set the MLflow tracking server URL
            mlflow.set_tracking_uri("http://localhost:5001")
            
            # Define maximum number of connection attempts
            max_retries = 5
            
            # Retry loop for MLflow connection
            for i in range(max_retries):
                try:
                    # Attempt to fetch all runs from experiment ID "1"
                    # This also serves as a connection test to MLflow
                    runs = mlflow.search_runs(experiment_ids=["1"])
                    
                    # If we successfully get runs, break the retry loop
                    if len(runs) > 0:
                        break
                except Exception as e:
                    # If this is our last retry attempt, re-raise the exception
                    if i == max_retries - 1:
                        raise
                    # Log warning and wait before next retry
                    logger.warning(f"Failed to connect to MLflow, retrying... ({i+1}/{max_retries})")
                    time.sleep(5)  # Wait 5 seconds before retrying
            
            # If we successfully connected but found no runs, that's an error condition
            if len(runs) == 0:
                raise Exception("No runs found in MLflow")
            
            latest_run = runs.sort_values("start_time", ascending=False).iloc[0]
            run_id = latest_run.run_id
            
            logger.info(f"Loading model from run {run_id}")
            self.model = mlflow.pyfunc.load_model(f"runs:/{run_id}/model")
            logger.info("Model loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading model and artifacts: {str(e)}")
            raise

    def setup_kafka(self) -> None:
        """
        Initialize Kafka connections:
        - Consumer: reads car listing data from 'cars-db.public.listings' topic
        - Producer: writes predictions to 'cars.public.predictions' topic
        
        Features:
        - Auto-commit enabled
        - JSON serialization/deserialization
        - Retry mechanism for producer
        
        Workflow:
        1. Database changes (car listings) are captured by Debezium/CDC
        2. Changes are published to 'cars-db.public.listings' Kafka topic
        3. This consumer reads those changes in real-time
        4. After prediction, results are published to 'cars.public.predictions'
        5. Other services can subscribe to predictions topic for further processing
        """
        try:
            # Get Kafka connection string from environment variables or use default
            KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            
            # Consumer setup for reading car listing changes
            # - 'earliest' offset ensures we process all messages from the beginning
            # - auto_commit tracks processed messages automatically
            # - group_id allows multiple instances to work as a consumer group
            # - consumer_timeout_ms determines how long to wait for new messages
            self.consumer = KafkaConsumer(
                'cars-db.public.listings',
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='car_price_predictor',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=1000
            )
            
            # Producer setup for publishing predictions
            # - retries=5 ensures resilience against temporary network issues
            # - value_serializer handles JSON conversion automatically
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                retries=5
            )
            
            logger.info("Kafka consumer and producer initialized")
            
        except Exception as e:
            logger.error(f"Error setting up Kafka: {str(e)}")
            raise

    def preprocess_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare raw car data for ML model:
        1. Convert data types for numeric fields
        2. Encode categorical variables using pre-trained label encoders
        3. Scale numeric variables using pre-trained scaler
        
        Args:
            data: Dictionary containing car features
            
        Returns:
            DataFrame with processed features ready for prediction
        """
        try:
            df = pd.DataFrame([data])
            
            numeric_columns = ['year', 'mileage', 'tax', 'mpg', 'engine_size']
            for col in numeric_columns:
                df[col] = df[col].astype(float)
                logger.info(f"Converted {col} to float")
            
            categorical_columns = ['model', 'transmission', 'fueltype']
            for column in categorical_columns:
                df[column] = self.label_encoders[column].transform(df[column])
                logger.info(f"Encoded {column}")
            
            df[numeric_columns] = self.scaler.transform(df[numeric_columns])
            logger.info("Scaled numeric columns")
            
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise

    def process_message(self, message: Any) -> Optional[Dict[str, Any]]:
        """
        Process individual Kafka messages:
        1. Extract car data from message
        2. Validate required fields
        3. Preprocess data
        4. Make prediction
        5. Add prediction metadata
        
        Args:
            message: Kafka message containing car data
            
        Returns:
            Dictionary with original data plus predictions, or None if processing fails
        """
        try:
            data = message.value if isinstance(message.value, dict) else json.loads(message.value)
            
            logger.info(f"Received message: {data}")
            if 'payload' in data and 'after' in data['payload']:
                car_data = data['payload']['after']
                logger.info(f"Extracted car data: {car_data}")
            else:
                car_data = data
                logger.info(f"Extracted car data: {car_data}")
            
            required_fields = ['model', 'year', 'transmission', 'mileage', 
                             'fueltype', 'tax', 'mpg', 'engine_size']
            
            for field in required_fields:
                if field not in car_data:
                    logger.warning(f"Missing required field: {field}")
                    return None
            
            processed_data = self.preprocess_data(car_data)
            logger.info(f"Processed data: {processed_data}")
            
            prediction = self.model.predict(processed_data)[0]
            logger.info(f"Prediction: {prediction}")
            
            car_data['predicted_price'] = float(prediction)
            logger.info(f"Predicted price: {car_data['predicted_price']}")
            
            car_data['prediction_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Prediction timestamp: {car_data['prediction_timestamp']}")
            
            return car_data
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None

    def run(self) -> None:
        """
        Main service loop:
        1. Continuously poll Kafka for new messages
        2. Process each message
        3. Send predictions back to Kafka
        4. Handle graceful shutdown
        
        Includes error handling and cleanup of Kafka connections
        """
        logger.info("Starting to consume messages...")
        
        while True:
            try:
                messages = self.consumer.poll(timeout_ms=1000)
                logger.info(f"Polled messages: {messages}")
                
                for topic_partition, msgs in messages.items():
                    for message in msgs:
                        result = self.process_message(message)
                        
                        if result:
                            self.producer.send('cars.public.predictions', value=result)
                            self.producer.flush()
                            
                            logger.info(
                                f"Processed car: {result.get('model', 'Unknown')} "
                                f"({result.get('year', 'Unknown')}). "
                                f"Predicted price: £{result['predicted_price']:,.2f}"
                            )
                
                time.sleep(0.1)
                    
            except KeyboardInterrupt:
                logger.info("Stopping the service...")
                break
                
            except Exception as e:
                logger.error(f"Error in processing loop: {str(e)}")
                time.sleep(5)  
        
        try:
            self.consumer.close()
            self.producer.close()
            logger.info("Kafka connections closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        
        logger.info("Service stopped")

def main():
    """
    Application entry point:
    1. Load environment variables
    2. Initialize predictor
    3. Load ML components
    4. Set up Kafka
    5. Start processing loop
    
    Includes comprehensive error handling and logging
    """
    try:
        load_dotenv()
        
        predictor = CarPricePredictor()
        
        predictor.load_model_and_artifacts()
        
        predictor.setup_kafka()
        
        predictor.run()
        
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        raise
    
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()