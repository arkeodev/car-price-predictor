-- Connect to default database first
\c postgres

-- Create databases
CREATE DATABASE mlflow;
CREATE DATABASE cars_db;

-- Connect to mlflow database and set up permissions
\c mlflow
GRANT ALL PRIVILEGES ON DATABASE mlflow TO postgres;
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO postgres;

-- Connect to cars_db and set up the listings table and permissions
\c cars_db

-- Create the listings table
CREATE TABLE IF NOT EXISTS listings (
    id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    year INTEGER,
    price DECIMAL,
    transmission VARCHAR(50),
    mileage INTEGER,
    fueltype VARCHAR(50),
    tax DECIMAL,
    mpg DECIMAL,
    engine_size DECIMAL,
    predicted_price DECIMAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions for cars_db
GRANT ALL PRIVILEGES ON DATABASE cars_db TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO postgres; 