# Technology Stack

## Backend Services

### FastAPI Backend

- **Framework**: FastAPI 0.100+
- **Language**: Python 3.9+
- **Features**:
  - Async request handling
  - Automatic OpenAPI documentation
  - Pydantic data validation
  - SQLAlchemy ORM integration

## Data Storage

### Primary Database

- **Database**: PostgreSQL 15
- **Features**:
  - Logical replication enabled
  - JSONB support
  - Full-text search
  - Transactional integrity

### Object Storage

- **Service**: MinIO
- **Usage**:
  - ML model artifacts storage
  - Large file storage
  - S3-compatible API

## Machine Learning Infrastructure

### MLflow

- **Version**: Latest
- **Components**:
  - Model Registry
  - Experiment Tracking
  - Model Serving
  - Artifact Storage

### ML Libraries

- scikit-learn
- pandas
- numpy
- Feature-engine

## Message Queue & Streaming

### Apache Kafka

- **Version**: 7.4.0
- **Usage**:
  - Event streaming
  - Real-time data pipeline
  - Service communication

### Debezium

- **Version**: 2.4
- **Purpose**: Change Data Capture
- **Integration**: PostgreSQL to Kafka

## Frontend

### Streamlit

- **Version**: Latest
- **Features**:
  - Interactive dashboards
  - Real-time updates
  - Data visualization
  - Form handling

### Visualization Libraries

- Plotly
- Matplotlib
- Seaborn

## Development & Operations

### Containerization

- Docker
- Docker Compose

### Monitoring & Management

- Redpanda Console (Kafka UI)
- Adminer (Database UI)
- MLflow UI
- MinIO Console

### Development Tools

- Git
- VS Code/PyCharm
- Python virtual environments
- Make
