# FastAPI Backend Application

A professional FastAPI backend application with PostgreSQL, Elasticsearch, and Selenium integration.

## Features

- User authentication and management
- PostgreSQL database integration
- Elasticsearch integration
- Selenium integration
- RESTful API endpoints
- JWT token authentication
- CORS middleware support

## Prerequisites

- Python 3.8+
- PostgreSQL
- Elasticsearch
- Docker (for running external services)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_db
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
SECRET_KEY=your-secret-key-here
```

5. Run the database migrations:
```bash
alembic upgrade head
```

6. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints/
├── core/
├── db/
├── models/
├── schemas/
├── services/
└── utils/
tests/
```

## Development

- The application uses SQLAlchemy for database operations
- Pydantic for data validation
- FastAPI for the web framework
- JWT for authentication
- Elasticsearch for search functionality
- Selenium for web automation

## License

MIT 