# Project File Structure

## Root Directory

```ascii
car-price-predictor/
├── .git/                           # Git repository
├── documents/                      # Project documentation
│   ├── api-endpoints.md           # API documentation
│   ├── app-flow.md               # Application flow
│   ├── database-structure.md     # Database schema
│   ├── file-structure.md        # This file
│   ├── frontend-screens.md      # UI/UX documentation
│   ├── machine-learning.md      # ML pipeline
│   ├── microservices-architecture.md # Architecture
│   ├── project-requirements.md  # Requirements
│   └── tech-stack.md           # Technology stack
├── backend/                      # FastAPI backend service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Main application
│   │   ├── config.py           # Configuration
│   │   ├── dependencies.py     # Dependencies
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API routes
│   │   ├── core/              # Core functionality
│   │   └── utils/             # Utilities
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── ml_service/                # ML training service
│   ├── src/
│   │   ├── __init__.py
│   │   ├── train.py          # Training script
│   │   ├── predict.py        # Prediction service
│   │   ├── features.py       # Feature engineering
│   │   ├── models.py         # Model definitions
│   │   └── utils.py          # Utilities
│   ├── tests/                # ML service tests
│   └── requirements.txt      # Python dependencies
├── streamlit_app/            # Streamlit frontend
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py           # Main application
│   │   ├── pages/           # Application pages
│   │   ├── components/      # UI components
│   │   └── utils/           # Utilities
│   ├── tests/               # Frontend tests
│   └── requirements.txt     # Python dependencies
├── data/                    # Data directory
│   ├── raw/                # Raw data
│   ├── processed/          # Processed data
│   └── external/           # External data
├── mlflow/                 # MLflow configuration
│   ├── Dockerfile         # MLflow container
│   └── mlflow.conf       # MLflow config
├── postgres/              # PostgreSQL
│   ├── init-schema.sql   # Database init
│   └── backup/           # Backup scripts
├── docker/               # Docker configuration
│   ├── backend/         # Backend Dockerfile
│   ├── ml_service/      # ML service Dockerfile
│   └── streamlit/       # Frontend Dockerfile
├── scripts/             # Utility scripts
│   ├── setup.sh        # Setup script
│   ├── deploy.sh       # Deployment script
│   └── backup.sh       # Backup script
├── tests/              # Integration tests
├── .env               # Environment variables
├── .gitignore        # Git ignore file
├── docker-compose.yml # Docker compose
├── README.md         # Project readme
└── requirements.txt  # Global dependencies
```

## Key Components

### 1. Backend Service

- FastAPI application structure
- Database models and schemas
- API endpoints and routing
- Core business logic

### 2. ML Service

- Training pipeline
- Prediction service
- Feature engineering
- Model management

### 3. Frontend Application

- Streamlit pages
- UI components
- State management
- API integration

### 4. Infrastructure

- Docker configuration
- Database setup
- MLflow configuration
- Deployment scripts

## Development Guidelines

### 1. Code Organization

- Modular structure
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive documentation

### 2. Testing Strategy

- Unit tests per component
- Integration tests
- End-to-end tests
- Performance tests

### 3. Documentation

- Code comments
- API documentation
- Architecture diagrams
- Setup instructions

### 4. Version Control

- Feature branches
- Pull request workflow
- Version tagging
- Change documentation

## Deployment Structure

### 1. Development

```ascii
development/
├── docker-compose.dev.yml
├── .env.dev
└── scripts/
    └── dev-setup.sh
```

### 2. Staging

```ascii
staging/
├── docker-compose.staging.yml
├── .env.staging
└── scripts/
    └── staging-deploy.sh
```

### 3. Production

```ascii
production/
├── docker-compose.prod.yml
├── .env.prod
└── scripts/
    └── prod-deploy.sh
```

## Configuration Management

### 1. Environment Variables

- Development settings
- Staging settings
- Production settings
- Secrets management

### 2. Application Config

- Service configuration
- Database settings
- API settings
- Logging configuration

### 3. Dependencies

- Python requirements
- System dependencies
- External services
- Version constraints
