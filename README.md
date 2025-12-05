# Beauty Salon Manager API

A backend API for managing beauty salon appointments, employees, services, and reporting.

## Quick Start

### Prerequisites
- Python 3.10+ or Docker
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Local Development

```bash
# Install dependencies
uv sync --dev

# Run server
uv run uvicorn app.main:app --reload
```

### Docker Development

```bash
docker-compose -f docker-compose.dev.yml up --build
```

Access API at: http://localhost:8000/docs

### Initial Setup

1. Create admin user: `POST /api/v1/auth/setup`
2. Login with HTTP Basic Auth
3. Create services, employees, schedules
4. Start booking visits!

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Secret for session signing (use `openssl rand -hex 32`) |
| `DATABASE_URL` | Yes | Database connection string |
| `DEBUG` | No | Enable debug mode (default: false) |

## Production Deployment

```bash
# Set required secrets
export SECRET_KEY=$(openssl rand -hex 32)

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Project Structure

```
app/
├── controllers/    # HTTP layer
├── services/       # Business logic
├── repositories/   # Data access
├── models/         # SQLAlchemy entities
├── schemas/        # Pydantic DTOs
└── core/           # Config, security, DI
```

## License

MIT
