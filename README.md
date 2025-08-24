# OpenMRS Bridge API

A FastAPI service that connects with OpenMRS database and provides a REST API for updating orders with API key authentication.

## Features

- 🔐 **API Key Authentication** - Secure API key-based authentication
- 🗄️ **MySQL Integration** - Direct connection to OpenMRS MySQL database
- 📝 **Orders Management** - Update orders using PUT and PATCH methods
- 🐳 **Docker Support** - Fully containerized with Docker and Docker Compose
- 📚 **Auto-generated Documentation** - Interactive API docs with Swagger UI
- 🔒 **Security** - CORS middleware and proper error handling

## Quick Start

### Prerequisites

- Docker and Docker Compose (for production)
- OpenMRS MySQL database access
- Python 3.11+ (for local development)

### Quick Commands

```bash
# Local Development (Recommended)
# Option 1: One-click start (Windows)
start_dev.bat

# Option 2: Python script with checks
python start_dev.py

# Option 3: Manual setup
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp env.example .env  # Edit with your database credentials
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload

# Docker (Production)
docker-compose up -d
```

### 1. Clone and Setup

```bash
git clone <repository-url>
cd bridge
cp env.example .env
```

### 2. Configure Environment

Edit `.env` file with your database credentials:

```env
# Database Configuration
DB_HOST=your_openmrs_db_host
DB_PORT=3306
DB_NAME=openmrs
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# API Configuration
API_KEYS=omrs_abc123def456ghi789,omrs_xyz789uvw456rst123

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Generate API Keys

You can generate API keys using the built-in endpoint:

```bash
curl -X POST http://localhost:1221/generate-api-key
```

Or use the provided format: `omrs_<32_random_chars>`

### 4. Run with Docker

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f openmrs-bridge
```

### 5. Access the API

- **API Documentation**: http://localhost:1221/docs
- **Health Check**: http://localhost:1221/health
- **API Base URL**: http://localhost:1221/api/v1

## API Endpoints

### Authentication

All endpoints require API key authentication using the `Authorization` header:

```
Authorization: Bearer <your_api_key>
```

### Orders Endpoints

#### Update Order (PATCH)
```http
PATCH /api/v1/orders/{uuid}
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "instructions": "Updated instructions",
  "urgency": "STAT"
}
```

#### Replace Order (PUT)
```http
PUT /api/v1/orders/{uuid}
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "order_type_id": 4,
  "concept_id": 18566,
  "orderer": 2,
  "encounter_id": 2,
  "creator": 5,
  "patient_id": 9,
  "uuid": "6000e165-57fd-4ad3-af48-0df1a6b157a9",
  "care_setting": 1,
  "instructions": "Complete order replacement"
}
```

#### Get Order
```http
GET /api/v1/orders/{uuid}
Authorization: Bearer <api_key>
```

**Note:** All endpoints now use UUID instead of order ID. UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

#### List Orders
```http
GET /api/v1/orders?skip=0&limit=100
Authorization: Bearer <api_key>
```

## Local Development

### Prerequisites

- Python 3.11 or higher
- MySQL database access (OpenMRS database)
- Git (for cloning the repository)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd bridge
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your actual database credentials
```

**Example `.env` file:**
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=openmrs
DB_USER=root
DB_PASSWORD=your_actual_password

# API Configuration
API_KEYS=omrs_abc123def456ghi789,omrs_xyz789uvw456rst123

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production

# Application Configuration
PORT=1221
HOST=0.0.0.0

# Debug mode for development
DEBUG=true
```

### 5. Start the Development Server

**Option 1: Using the start script (Recommended)**
```bash
# Run the development server with automatic checks
python start_dev.py
```

**Option 2: Manual start**
```bash
# Start the FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload
```

**Server Options:**
- `--host 0.0.0.0`: Makes the server accessible from other devices on the network
- `--port 1221`: Runs the server on port 1221
- `--reload`: Automatically restarts the server when code changes are detected

### 6. Verify the Server is Running

You should see output similar to:
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\oonions\\Documents\\QA projects\\bridge']
INFO:     Uvicorn running on http://0.0.0.0:1221 (Press CTRL+C to quit)
INFO:     Started reloader process [39208] using WatchFiles
INFO:     Started server process [3664]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Access Your Application

- **API Documentation (Swagger UI)**: http://localhost:1221/docs
- **Health Check**: http://localhost:1221/health
- **API Base URL**: http://localhost:1221/api/v1

### Development Workflow

#### Starting Development
```bash
# 1. Activate virtual environment (if not already active)
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 2. Start the development server
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload
```

#### Stopping the Server
```bash
# Press Ctrl+C in the terminal where the server is running
```

#### Making Changes
- The server will automatically reload when you save changes to Python files
- You'll see reload messages in the terminal
- No need to manually restart the server

#### Testing Your Changes
```bash
# Run the test script
python test_api.py

# Or test individual endpoints
curl http://localhost:1221/health
curl http://localhost:1221/docs
```

### Troubleshooting

#### Port Already in Use
If port 1221 is already in use:
```bash
# Use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or find and kill the process using port 1221
netstat -ano | findstr :1221  # Windows
lsof -i :1221  # macOS/Linux
```

#### Database Connection Issues
```bash
# Check if your .env file has correct database credentials
# Ensure MySQL server is running
# Test database connection manually
```

#### Virtual Environment Issues
```bash
# If virtual environment is corrupted, recreate it
deactivate  # if active
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### Import Errors
```bash
# Ensure you're in the correct directory
pwd  # Check current directory
ls app/  # Should show Python files

# Check Python path
python -c "import sys; print(sys.path)"
```

### Development Tips

1. **Use the API Documentation**: Visit http://localhost:1221/docs to test endpoints interactively
2. **Monitor Logs**: Watch the terminal output for request logs and errors
3. **Hot Reload**: The `--reload` flag automatically restarts the server when you save changes
4. **Environment Variables**: Use the `.env` file for configuration, never commit sensitive data
5. **Testing**: Use the provided `test_api.py` script to verify functionality

### Alternative Start Commands

```bash
# Development with more verbose logging
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload --log-level debug

# Production-like settings (no reload)
uvicorn app.main:app --host 0.0.0.0 --port 1221 --workers 1

# Run from Python directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload
```

## Project Structure

```
bridge/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── crud.py              # Database operations
│   └── api/
│       ├── __init__.py
│       └── orders.py        # Orders endpoints
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── env.example             # Environment variables example
└── README.md               # This file
```

## Security Features

### API Key Management

- **Format**: `omrs_<32_random_hex_chars>`
- **Storage**: Environment variables (comma-separated)
- **Validation**: Bearer token authentication
- **Generation**: Built-in endpoint for key generation

### Database Security

- Connection pooling with automatic reconnection
- Parameterized queries to prevent SQL injection
- Non-root user in Docker container

## Error Handling

The API provides consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Additional details"
}
```

Common HTTP status codes:
- `200` - Success
- `401` - Unauthorized (invalid API key)
- `404` - Order not found
- `422` - Validation error
- `500` - Internal server error

## Monitoring

### Health Check

```bash
curl http://localhost:1221/health
```

Response:
```json
{
  "status": "healthy",
  "service": "OpenMRS Bridge API",
  "version": "1.0.0"
}
```

### Logs

View application logs:

```bash
# Docker
docker-compose logs -f openmrs-bridge

# Local
tail -f logs/app.log
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify database credentials in `.env`
   - Ensure MySQL server is running
   - Check network connectivity

2. **API Key Authentication Failed**
   - Verify API key format: `omrs_<32_chars>`
   - Check `API_KEYS` environment variable
   - Ensure `Authorization: Bearer <key>` header

3. **Port Already in Use**
   - Change port in `.env` file
   - Update `docker-compose.yml` if using Docker

### Debug Mode

Enable debug mode by setting:

```env
DEBUG=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Create an issue in the repository 