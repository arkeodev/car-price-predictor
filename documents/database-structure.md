# Database Structure

## Overview

The application uses PostgreSQL as its primary database, with logical replication enabled for change data capture.

## Schemas

### Main Schema: public

#### Table: cars

```sql
CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    fuel_type VARCHAR(50) NOT NULL,
    transmission VARCHAR(50) NOT NULL,
    engine_size FLOAT NOT NULL,
    price FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cars_make_model ON cars(make, model);
CREATE INDEX idx_cars_year ON cars(year);
CREATE INDEX idx_cars_price ON cars(price);
```

#### Table: predictions

```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    car_id INTEGER REFERENCES cars(id),
    predicted_price FLOAT NOT NULL,
    confidence_lower FLOAT NOT NULL,
    confidence_upper FLOAT NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
);

CREATE INDEX idx_predictions_car_id ON predictions(car_id);
CREATE INDEX idx_predictions_model_version ON predictions(model_version);
```

#### Table: model_metrics

```sql
CREATE TABLE model_metrics (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(100) NOT NULL,
    mae FLOAT NOT NULL,
    mse FLOAT NOT NULL,
    rmse FLOAT NOT NULL,
    r2_score FLOAT NOT NULL,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT false
);

CREATE INDEX idx_model_metrics_version ON model_metrics(model_version);
CREATE INDEX idx_model_metrics_active ON model_metrics(is_active);
```

## MLflow Schema: mlflow

Used by MLflow for experiment tracking and model registry.

```sql
-- MLflow automatically creates its schema and tables
CREATE DATABASE mlflow;
```

## Indexes and Constraints

### Primary Keys

- `cars.id`
- `predictions.id`
- `model_metrics.id`

### Foreign Keys

- `predictions.car_id` → `cars.id`

### Indexes

- `idx_cars_make_model`
- `idx_cars_year`
- `idx_cars_price`
- `idx_predictions_car_id`
- `idx_predictions_model_version`
- `idx_model_metrics_version`
- `idx_model_metrics_active`

## Data Types

### Common Types Used

- `VARCHAR`: For string fields
- `INTEGER`: For whole numbers
- `FLOAT`: For decimal numbers
- `TIMESTAMP WITH TIME ZONE`: For timestamps
- `BOOLEAN`: For true/false flags
- `SERIAL`: For auto-incrementing IDs

## Triggers

### Update Timestamp Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cars_updated_at
    BEFORE UPDATE ON cars
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Views

### Active Model View

```sql
CREATE VIEW active_model AS
SELECT *
FROM model_metrics
WHERE is_active = true
ORDER BY training_date DESC
LIMIT 1;
```

### Recent Predictions View

```sql
CREATE VIEW recent_predictions AS
SELECT 
    p.*,
    c.make,
    c.model,
    c.year,
    c.mileage
FROM predictions p
JOIN cars c ON p.car_id = c.id
ORDER BY p.created_at DESC
LIMIT 100;
```

## Backup and Recovery

- Daily backups configured
- Point-in-time recovery enabled
- Logical replication for CDC
- WAL archiving enabled
