# Development Environment Setup

This guide covers setting up the development environment for the multi-tenant financial tools API.

## Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose**
- **Git**
- **Make** (optional, for convenience scripts)

## Quick Start with Docker

### 1. Clone Repository
```bash
git clone <repository-url>
cd finance-tool-api/backend
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/fastapi_dev

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-super-secret-key-here-at-least-32-characters-long
ENCRYPTION_KEY=your-encryption-key-here

# Stripe (for subscription testing)
STRIPE_API_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# LLM Integration
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key

# Environment
ENVIRONMENT=development
DEBUG=true
```

### 3. Start Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 4. Database Migration
```bash
# Run database migrations
docker-compose exec app alembic upgrade head

# Or run inside container
docker-compose exec app bash
# Inside container: alembic upgrade head
```

### 5. Verify Setup
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs
```

## Manual Setup (Without Docker)

### 1. Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Install optional finance dependencies
pip install -e .[finance]
```

### 2. Database Setup
```bash
# Install PostgreSQL locally or use Docker
docker run -d \
  --name postgres-dev \
  -e POSTGRES_DB=fastapi_dev \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=pass \
  -p 5432:5432 \
  postgres:15

# Install Redis locally or use Docker
docker run -d \
  --name redis-dev \
  -p 6379:6379 \
  redis:7-alpine
```

### 3. Database Migration
```bash
# Initialize database
alembic upgrade head
```

### 4. Start Application
```bash
# Development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or with workers (production-like)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Development Workflow

### Code Changes
```bash
# The application uses hot reload in development
# Changes to .py files will automatically restart the server

# For Docker development:
docker-compose up --build  # Rebuilds on code changes
```

### Database Changes
```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth/test_auth.py

# Run tests in watch mode
pytest-watch
```

### Code Quality
```bash
# Lint code
ruff check src/

# Format code
ruff format src/

# Type checking
mypy src/

# Pre-commit hooks
pre-commit run --all-files
```

## API Testing

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs

# OpenAPI schema
curl http://localhost:8000/openapi.json
```

### Using HTTPie
```bash
# Install HTTPie
pip install httpie

# Test endpoints
http GET http://localhost:8000/health
http GET http://localhost:8000/docs
```

### Using Postman/Insomnia
Import the OpenAPI schema from `http://localhost:8000/openapi.json`

## Debugging

### Application Logs
```bash
# Docker logs
docker-compose logs -f app

# Application logs (when running manually)
tail -f logs/app.log
```

### Database Inspection
```bash
# Connect to database
docker-compose exec db psql -U user -d fastapi_dev

# View tables
\d

# Query data
SELECT * FROM user LIMIT 5;
```

### Redis Inspection
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View keys
KEYS *

# Monitor commands
MONITOR
```

## Environment Configuration

### Development vs Production
```bash
# Development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### External Services

#### Stripe Testing
```bash
# Use Stripe test keys
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Test webhook endpoint
stripe listen --forward-to localhost:8000/webhooks/stripe
```

#### OpenRouter API
```bash
# Get API key from https://openrouter.ai/
OPENROUTER_API_KEY=sk-or-v1-...

# Test LLM integration
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"user_id": "550e8400-e29b-41d4-a716-446655440001", "message": "Hello"}'
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn src.main:app --port 8001
```

#### Database Connection Issues
```bash
# Check database status
docker-compose ps db

# Restart database
docker-compose restart db

# Rebuild database
docker-compose down -v
docker-compose up -d db
```

#### Migration Issues
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head

# Force recreate database
docker-compose down -v
docker-compose up -d
```

### Performance Optimization

#### Development Settings
```bash
# Enable SQL query logging
DATABASE_ECHO=true

# Disable rate limiting for testing
RATE_LIMIT_TIMES=1000
RATE_LIMIT_SECONDS=1
```

## Next Steps

1. **Explore API**: Visit `http://localhost:8000/docs`
2. **Run Tests**: Execute `pytest` to verify functionality
3. **Add Features**: Start developing new endpoints
4. **Monitor Logs**: Use `docker-compose logs -f` for debugging

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Stripe Testing](https://stripe.com/docs/testing)
- [OpenRouter API](https://openrouter.ai/docs)