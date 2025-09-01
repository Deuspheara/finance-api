# Multi-Tenant Financial Tools API Documentation

## Overview

This is a comprehensive FastAPI-based system that provides multi-tenant financial tools with subscription management, LLM chat functionality, and GDPR compliance features.

## Features

- **Multi-Tenant Architecture**: Complete user isolation and data segregation
- **Subscription Management**: Tiered subscription system with Stripe integration
- **Financial Tools**: Portfolio analysis with usage limits
- **LLM Chat**: AI-powered conversational interface with context management
- **GDPR Compliance**: Data export, anonymization, and consent management
- **Authentication**: JWT-based authentication with secure token management
- **Monitoring**: Prometheus metrics and health checks
- **Rate Limiting**: Configurable rate limits per user and endpoint

## Architecture

The system is built with:
- **FastAPI**: High-performance async web framework
- **SQLModel**: SQL database ORM with Pydantic integration
- **PostgreSQL**: Primary database for user data and subscriptions
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **Stripe**: Payment processing and subscription management
- **OpenRouter**: LLM API integration

## API Structure

All API endpoints are versioned under `/api/v1/` prefix:

- **Authentication**: `/auth/*`
- **Subscriptions**: `/api/v1/subscription/*`
- **Finance Tools**: `/api/v1/finance/*`
- **LLM Chat**: `/api/v1/llm/*`
- **Privacy/GDPR**: `/api/v1/privacy/*`

## Subscription Tiers

### Free Tier
- Portfolio analyses: 5 per month
- LLM requests: 10 per month

### Premium Tier
- Portfolio analyses: 100 per month
- LLM requests: 1000 per month
- Priority support

## Quick Start

1. **Development Setup**: See [setup/development.md](setup/development.md)
2. **Production Setup**: See [setup/production.md](setup/production.md)
3. **API Examples**: See [examples/](examples/) directory

## API Documentation

- [Authentication](api/authentication.md)
- [Subscription Management](api/subscriptions.md)
- [Finance Tools](api/finance.md)
- [LLM Chat](api/llm.md)
- [Privacy & GDPR](api/privacy.md)

## Security

- JWT token authentication
- User data isolation
- Rate limiting
- Input validation
- CORS configuration
- Environment-based configuration

## Monitoring

- Health checks: `GET /health`
- Metrics: `GET /metrics` (Prometheus format)
- Structured logging with configurable levels

## Environment Variables

See [setup/development.md](setup/development.md) for complete environment configuration.

## Support

For API support and integration questions, refer to the specific API documentation sections.