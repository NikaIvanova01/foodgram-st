# Foodgram - Your Recipe Management Platform

## Project Description
Foodgram is a recipe management service where users can share recipes, follow other users, and create shopping lists from recipe ingredients.

## Technology Stack
- Backend: Python/Django
- Frontend: React
- Database: PostgreSQL
- Server: Nginx
- Containerization: Docker

## Project Structure
```
├── backend/          # Django backend application
├── frontend/         # React frontend application
├── infra/            # Infrastructure configuration files
├── data/             # Initial data and fixtures
└── docs/             # API documentation
```

## Features
- User authentication and authorization
- Create, view, edit and delete recipes
- Add recipes to favorites
- Create shopping lists from recipes
- Follow other users
- Filter recipes by tags

## Docker Images
The project's Docker images are available at:
- Backend: `https://hub.docker.com/r/nikaivanova/foodgram-backend`
- Frontend: `https://hub.docker.com/r/nikaivanova/foodgram-frontend`

You can pull these images directly instead of building them locally:
```bash
docker pull nikaivanova/foodgram-backend:latest
docker pull nikaivanova/foodgram-frontend:latest
```

Our docker-compose.yml already configured to use these images:
```yaml
services:
  frontend:
    image: nikaivanova/foodgram-frontend:latest
    ...

  backend:
    image: nikaivanova/foodgram-backend:latest
    ...
```

## Environment Variables
The project uses environment variables for configuration. Sample configuration files are provided in `.env.sample`:

### Required Environment Variables:
```bash
# Debug mode (0 for production, 1 for development)
DEBUG=0

# Django secret key
SECRET_KEY=django-insecure-token-yo

# Allowed hosts for the application
ALLOWED_HOSTS=127.0.0.1,backend,localhost,foodgram-backend

# Database configuration
DB_NAME=foodgram-db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=foodgram-postgres
DB_PORT=5432
```

To set up your environment:
1. In thr project directory, copy the sample file:
```bash
cp infra/.env.sample infra/.env
```
2. Update the values in `.env` with your actual configuration

## Installation and Setup

### Prerequisites
- Docker
- Docker Compose

### Development Setup
1. Clone the repository
   ```bash
   git clone https://github.com/savlagood/foodgram-st.git
   ```
2. Create environment files as described above
3. Run the containers with published images:
   ```bash
   cd foodgram-st/infra
   docker-compose up -d
   ```
4. Apply migrations:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```
5. Load initial data:
   ```bash
   docker-compose exec backend python manage.py load_ingredients data/ingredients.json
   ```
6. Create superuser:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

### Building and Publishing Docker Images
If you want to build and publish your own Docker images:

1. Make sure you're logged into Docker Hub:
   ```bash
   docker login
   ```

2. Build and push the images:
   ```bash
   docker build -t your-username/foodgram-frontend:latest ./frontend
   docker push your-username/foodgram-frontend:latest

   docker build -t your-username/foodgram-backend:latest ./backend
   docker push your-username/foodgram-backend:latest
   ```

3. Update the docker-compose.yml to use your images:
   ```yaml
   services:
     frontend:
       image: your-username/foodgram-frontend:latest
       ...

     backend:
       image: your-username/foodgram-backend:latest
       ...
   ```

### API Documentation
API documentation is available at [`/api/docs/`](http://127.0.0.1/api/docs/) after starting the project.
You can find the OpenAPI schema in `docs/openapi-schema.yml`.

### Testing
The project includes a Postman collection for API testing located in `postman_collection/foodgram.postman_collection.json`.

## About Author
- Иванова Вероника Петровна
- НИУ МЭИ - ИВТИ - А-08-22
