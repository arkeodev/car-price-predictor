# Import required libraries and modules
import six
import sys
# Fix for Python 3.12 compatibility with kafka
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
import json
import logging
from contextlib import contextmanager
import threading
import time

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with title
app = FastAPI(title="Car Price Prediction API")

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database configuration
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/cars_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC_LISTINGS = "cars-db.public.listings"
KAFKA_TOPIC_PREDICTIONS = "cars.public.predictions"

# Define SQLAlchemy model for the Car table
class Car(Base):
    """
    SQLAlchemy model representing a car listing in the database
    Includes all relevant car attributes and timestamps
    """
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    year = Column(Integer)
    price = Column(Float)
    transmission = Column(String)
    mileage = Column(Integer)
    fueltype = Column(String)
    tax = Column(Float)
    mpg = Column(Float)
    engine_size = Column(Float)
    predicted_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Define Pydantic models for request/response validation
class CarBase(BaseModel):
    """
    Base Pydantic model for car data validation
    Includes field validation and examples for API documentation
    """
    model: str = Field(..., example="Fiesta")
    year: int = Field(..., ge=1900, le=datetime.now().year, example=2019)
    price: float = Field(..., gt=0, example=12000)
    transmission: str = Field(..., example="Manual")
    mileage: int = Field(..., ge=0, example=25000)
    fueltype: str = Field(..., example="Petrol")
    tax: float = Field(..., ge=0, example=145)
    mpg: float = Field(..., ge=0, example=55.4)
    engine_size: float = Field(..., gt=0, example=1.0)

    @validator('transmission')
    def validate_transmission(cls, v):
        """Validate transmission type against allowed values"""
        allowed = {'Manual', 'Automatic', 'Semi-Auto'}
        if v not in allowed:
            raise ValueError(f'transmission must be one of {allowed}')
        return v

    @validator('fueltype')
    def validate_fuel_type(cls, v):
        """Validate fuel type against allowed values"""
        allowed = {'Petrol', 'Diesel', 'Hybrid', 'Electric'}
        if v not in allowed:
            raise ValueError(f'fueltype must be one of {allowed}')
        return v

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: int
    predicted_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class KafkaManager:
    """
    Manages Kafka producer and consumer connections.
    Implements the Singleton pattern to ensure only one instance of producer/consumer exists.
    """
    _producer = None
    _consumer = None
    _consumer_thread = None
    _running = False

    @classmethod
    def get_producer(cls):
        """Returns a singleton instance of KafkaProducer"""
        if cls._producer is None:
            logger.info("Initializing Kafka producer connection to %s", KAFKA_BOOTSTRAP_SERVERS)
            try:
                cls._producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8')
                )
                logger.info("✅ Kafka producer successfully initialized")
            except Exception as e:
                logger.error("❌ Failed to initialize Kafka producer: %s", str(e))
                raise
        return cls._producer

    @classmethod
    def start_consumer(cls):
        """Starts the Kafka consumer in a background thread"""
        if cls._consumer_thread is None:
            logger.info("Starting Kafka consumer thread")
            try:
                cls._running = True
                cls._consumer_thread = threading.Thread(target=cls._consume_predictions)
                cls._consumer_thread.daemon = True
                cls._consumer_thread.start()
                logger.info("✅ Kafka consumer thread started successfully")
            except Exception as e:
                logger.error("❌ Failed to start Kafka consumer thread: %s", str(e))
                raise

    @classmethod
    def _consume_predictions(cls):
        """Background task for consuming predictions from Kafka"""
        logger.info("Initializing Kafka consumer for topic: %s", KAFKA_TOPIC_PREDICTIONS)
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC_PREDICTIONS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='backend-consumer'
            )
            logger.info("✅ Kafka consumer successfully initialized")
        except Exception as e:
            logger.error("❌ Failed to initialize Kafka consumer: %s", str(e))
            return

        message_count = 0
        error_count = 0
        
        while cls._running:
            try:
                messages = consumer.poll(timeout_ms=1000)
                if messages:
                    for topic_partition, msgs in messages.items():
                        partition = topic_partition.partition
                        logger.debug(
                            "Received %d messages from partition %d", 
                            len(msgs), 
                            partition
                        )
                        for message in msgs:
                            message_count += 1
                            logger.info(
                                "Processing prediction message %d (offset=%d, partition=%d)",
                                message_count,
                                message.offset,
                                partition
                            )
                            cls._handle_prediction(message.value)
                            
            except Exception as e:
                error_count += 1
                logger.error(
                    "❌ Error consuming messages (attempt %d): %s", 
                    error_count, 
                    str(e)
                )
                if error_count >= 3:
                    logger.critical(
                        "Multiple consumer errors occurred. Waiting 30 seconds before retrying..."
                    )
                    time.sleep(30)
                    error_count = 0
                else:
                    time.sleep(5)

        logger.info("Closing Kafka consumer (processed %d messages total)", message_count)
        consumer.close()

    @classmethod
    def _handle_prediction(cls, prediction_data):
        """Handles incoming prediction messages"""
        try:
            car_id = prediction_data.get('id')
            predicted_price = prediction_data.get('predicted_price')
            
            if not car_id or not predicted_price:
                logger.warning("❌ Received invalid prediction data: %s", prediction_data)
                return
                
            logger.debug(
                "Processing prediction for car %d: £%,.2f", 
                car_id, 
                predicted_price
            )
            
            with get_db() as db:
                car = db.query(Car).filter(Car.id == car_id).first()
                if car:
                    car.predicted_price = predicted_price
                    db.commit()
                    logger.info(
                        "✅ Updated prediction for car %d: £%,.2f (model=%s, year=%d)",
                        car_id,
                        predicted_price,
                        car.model,
                        car.year
                    )
                else:
                    logger.warning(
                        "❌ Car %d not found in database for prediction update",
                        car_id
                    )
                    
        except Exception as e:
            logger.error(
                "❌ Error handling prediction for car %d: %s",
                prediction_data.get('id', 'unknown'),
                str(e)
            )

# Routes
@app.get("/cars", response_model=List[CarResponse])
def get_cars():
    with get_db() as db:
        logger.info("Fetching all cars from database")
        cars = db.query(Car).all()
        logger.info("✅ Fetched %d cars from database", len(cars))
        return cars

@app.post("/cars", response_model=CarResponse)
def create_car(car: CarCreate):
    """
    Creates a new car listing and sends it to Kafka

    Flow:
    1. Save car details to database
    2. Send car data to Kafka topic for ML processing
    3. ML service will process it and send back prediction via another topic
    4. Background consumer will update the database with the prediction    
    """
    logger.info(
        "Creating new car listing (model=%s, year=%d, price=£%.2f)",
        car.model,
        car.year,
        car.price
    )
    
    with get_db() as db:
        try:
            # Save to database
            db_car = Car(**car.dict())
            db.add(db_car)
            db.commit()
            db.refresh(db_car)
            logger.info("✅ Saved car %d to database", db_car.id)
            
            # Prepare serializable dictionary for Kafka
            kafka_data = {
                "id": db_car.id,
                "model": db_car.model,
                "year": db_car.year,
                "price": db_car.price,
                "transmission": db_car.transmission,
                "mileage": db_car.mileage,
                "fueltype": db_car.fueltype,
                "tax": db_car.tax,
                "mpg": db_car.mpg,
                "engine_size": db_car.engine_size,
                "created_at": db_car.created_at.isoformat(),
                "updated_at": db_car.updated_at.isoformat()
            }
            
            # Send to Kafka
            try:
                producer = KafkaManager.get_producer()
                producer.send(KAFKA_TOPIC_LISTINGS, kafka_data)
                producer.flush()
                logger.info(
                    "✅ Sent car %d to Kafka topic: %s",
                    db_car.id,
                    KAFKA_TOPIC_LISTINGS
                )
            except Exception as e:
                logger.error(
                    "❌ Failed to send car %d to Kafka: %s",
                    db_car.id,
                    str(e)
                )
            
            return db_car
            
        except Exception as e:
            logger.error("❌ Failed to create car listing: %s", str(e))
            raise HTTPException(
                status_code=500,
                detail="Failed to create car listing"
            )

@app.get("/cars/{car_id}", response_model=CarResponse)
def get_car(car_id: int):
    with get_db() as db:
        car = db.query(Car).filter(Car.id == car_id).first()
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")
        return car

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if engine.connect() else "disconnected"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and start Kafka consumer on application startup"""
    logger.info("🚀 Starting application...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
        
        KafkaManager.start_consumer()
        logger.info("✅ Kafka consumer started")
        
        logger.info("✅ Application startup complete")
    except Exception as e:
        logger.error("❌ Application startup failed: %s", str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown Kafka consumer and producer"""
    logger.info("🛑 Shutting down application...")
    try:
        KafkaManager._running = False
        if KafkaManager._consumer_thread:
            logger.info("Waiting for Kafka consumer thread to stop...")
            KafkaManager._consumer_thread.join(timeout=5)
            logger.info("✅ Kafka consumer thread stopped")
            
        if KafkaManager._producer:
            logger.info("Closing Kafka producer...")
            KafkaManager._producer.close()
            logger.info("✅ Kafka producer closed")
            
        logger.info("✅ Application shutdown complete")
    except Exception as e:
        logger.error("❌ Error during shutdown: %s", str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)