# FastAPI 2025 Production Template

A modern, production-ready FastAPI application template with the latest best practices and technologies for 2025.

## 🚀 Tech Stack

- **Python**: 3.12 (LTS recommended)
- **FastAPI**: 0.116.1+ with `fastapi[standard]`
- **SQLModel**: 0.0.24+ (SQLAlchemy 2.0 + Pydantic V2)
- **PostgreSQL**: 15+ with AsyncPG
- **Redis**: 7.4+ for caching
- **Docker**: Multi-stage builds with Debian 12 Bookworm
- **Gunicorn + Uvicorn**: Production WSGI/ASGI server

## 📁 Project Structure

```
fastapi-project/
├── .github/workflows/        # CI/CD pipelines
├── docker/                   # Docker configurations
├── src/                      # Application source code
│   ├── core/                 # Core configurations
│   ├── auth/                 # Authentication domain
│   ├── users/                # Users domain
│   └── shared/               # Shared utilities
├── tests/                    # Test suite
├── alembic/                  # Database migrations
└── scripts/                  # Deployment scripts
```

## 🛠 Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7.4+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup environment:**
   ```bash
   git clone <your-repo>
   cd fastapi-project
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .[dev]
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the development server:**
   ```bash
   fastapi dev src/main.py
   ```

### Docker Development

1. **Start all services:**
   ```bash
   docker-compose up
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

The API will be available at `http://localhost:8000`

## 🚢 Production Deployment

### Docker Production

1. **Build production image:**
   ```bash
   docker build -f docker/Dockerfile.prod -t fastapi-app:latest .
   ```

2. **Deploy with docker-compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `SECRET_KEY`: JWT signing key (32+ characters)
- `ENVIRONMENT`: `development` | `staging` | `production`

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## 📊 API Documentation

- **Swagger UI**: `http://localhost:8000/docs` (development only)
- **ReDoc**: `http://localhost:8000/redoc` (development only)

## 🔍 Code Quality

### Linting and Formatting

```bash
ruff check .        # Lint code
ruff format .       # Format code
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## 📝 API Endpoints

### Health Checks
- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness probe (DB + Redis)
- `GET /health/live` - Liveness probe

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Users
- `POST /users/` - Create user
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS middleware
- Trusted host middleware
- Rate limiting
- Input validation with Pydantic
- SQL injection prevention

## 🗄 Database

### Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## 📈 Monitoring

- Health check endpoints for container orchestration
- Structured logging (JSON in production)
- Metrics support with Prometheus (configurable)

## 🚀 Key 2025 Updates

- **Uvicorn Workers**: Updated to `uvicorn-worker` package
- **Python 3.12**: LTS version with performance improvements
- **FastAPI CLI**: Uses `fastapi run` and `fastapi dev`
- **SQLAlchemy 2.0**: Modern async syntax
- **Pydantic V2**: Latest validation and serialization
- **Container Security**: Non-root user, multi-stage builds

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Use conventional commits

## 📄 License

MIT License - see LICENSE file for details.