# API Endpoints Documentation

## Base URL

```bash
http://localhost:8000
```

## Authentication

- Currently no authentication required for development
- Production deployment should implement appropriate authentication

## Car Management Endpoints

### List Cars

```http
GET /cars
```

- **Query Parameters**:
  - `page`: int (default: 1)
  - `limit`: int (default: 10)
  - `sort_by`: string (default: "id")
  - `order`: string (asc/desc)
- **Response**: List of car objects with pagination metadata

### Get Single Car

```http
GET /cars/{car_id}
```

- **Path Parameters**:
  - `car_id`: int
- **Response**: Detailed car object

### Create Car

```http
POST /cars
```

- **Request Body**:

  ```json
  {
    "make": string,
    "model": string,
    "year": int,
    "mileage": int,
    "fuel_type": string,
    "transmission": string,
    "engine_size": float,
    "price": float
  }
  ```

- **Response**: Created car object

### Update Car

```http
PUT /cars/{car_id}
```

- **Path Parameters**:
  - `car_id`: int
- **Request Body**: Same as Create Car
- **Response**: Updated car object

### Delete Car

```http
DELETE /cars/{car_id}
```

- **Path Parameters**:
  - `car_id`: int
- **Response**: Success message

## Price Prediction Endpoints

### Predict Price

```http
POST /predict
```

- **Request Body**:

  ```json
  {
    "make": string,
    "model": string,
    "year": int,
    "mileage": int,
    "fuel_type": string,
    "transmission": string,
    "engine_size": float
  }
  ```

- **Response**:

  ```json
  {
    "predicted_price": float,
    "confidence_interval": {
      "lower": float,
      "upper": float
    },
    "model_version": string
  }
  ```

### Batch Predict

```http
POST /predict/batch
```

- **Request Body**: Array of prediction requests
- **Response**: Array of predictions

## Model Management Endpoints

### Get Model Info

```http
GET /model/info
```

- **Response**: Current model metadata

### Model Health

```http
GET /model/health
```

- **Response**: Model health status

## System Endpoints

### Health Check

```http
GET /health
```

- **Response**: Service health status

### Version

```http
GET /version
```

- **Response**: API version information

## Error Responses

All endpoints follow standard HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

Error Response Format:

```json
{
  "error": string,
  "detail": string,
  "status_code": int
}
```
