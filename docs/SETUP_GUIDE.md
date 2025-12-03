# OpenMRS Bridge API - Step-by-Step Setup Guide

This guide will walk you through setting up the OpenMRS Bridge API service from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Setup](#docker-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL/MariaDB** - Access to an OpenMRS database (can be local or remote)
- **Git** - For cloning the repository (if applicable)

### Optional (for Docker setup)

- **Docker Desktop** - [Download Docker](https://www.docker.com/products/docker-desktop/)
- **Docker Compose** - Usually included with Docker Desktop

### Verify Prerequisites

```bash
# Check Python version
python --version
# Should show Python 3.11.x or higher

# Check if pip is installed
pip --version

# Check if Docker is installed (optional)
docker --version
docker-compose --version
```

---

## Local Development Setup

### Step 1: Navigate to Project Directory

```bash
cd "C:\Users\oonions\Documents\QA projects\omrs-bridge"
```

### Step 2: Create Virtual Environment

A virtual environment isolates your project dependencies from other Python projects.

**Windows:**
```bash
python -m venv venv
```

**macOS/Linux:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

### Step 4: Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- SQLAlchemy (database ORM)
- PyMySQL (MySQL driver)
- Pydantic (data validation)
- And other dependencies

**Expected output:** You should see packages being downloaded and installed. Wait for the process to complete.

### Step 5: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   # Windows
   copy env.example .env
   
   # macOS/Linux
   cp env.example .env
   ```

2. **Edit the `.env` file** with your actual database credentials:

   Open `.env` in a text editor and update the following values:

   ```env
   # Database Configuration
   DB_HOST=localhost              # Your MySQL host (or IP address)
   DB_PORT=3306                   # MySQL port (usually 3306)
   DB_NAME=openmrs                # Your OpenMRS database name
   DB_USER=your_database_user     # Your MySQL username
   DB_PASSWORD=your_password      # Your MySQL password
   
   # OpenMRS REST Configuration (optional, for search index updates)
   OPENMRS_BASE_URL=http://localhost:8080/openmrs
   OPENMRS_REST_USERNAME=admin
   OPENMRS_REST_PASSWORD=Admin123
   OPENMRS_REST_TIMEOUT_SECONDS=10.0
   OPENMRS_REST_VERIFY_SSL=true
   
   # API Configuration
   # Comma-separated list of valid API keys
   API_KEYS=omrs_abc123def456ghi789,omrs_xyz789uvw456rst123
   
   # Security Configuration
   SECRET_KEY=your-super-secret-key-change-this-in-production
   
   # Application Configuration
   PORT=1221                       # Port to run the API on
   HOST=0.0.0.0                   # Host to bind to
   
   # Performance Settings
   DEBUG=false                     # Set to true for development
   PRODUCTION=false
   ```

   **Important Notes:**
   - Replace `your_database_user` and `your_password` with your actual MySQL credentials
   - If your database is on a remote server, update `DB_HOST` with the server's IP or hostname
   - Generate secure API keys (see Step 6)
   - Change `SECRET_KEY` to a random, secure string

### Step 6: Generate API Keys (Optional)

You can generate API keys using the built-in endpoint after starting the server, or create them manually:

**Format:** `omrs_` followed by 32 random hexadecimal characters

**Example:**
```
omrs_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

You can generate one using Python:
```bash
python -c "import secrets; print('omrs_' + secrets.token_hex(16))"
```

Add multiple API keys separated by commas in the `API_KEYS` environment variable.

### Step 7: Start the Development Server

You have three options to start the server:

#### Option 1: Using the Start Script (Recommended - Windows)
```bash
scripts\start_dev.bat
```

#### Option 2: Using the Python Start Script (Recommended - Cross-platform)
```bash
python scripts/start_dev.py
```

This script will:
- ✅ Check Python version
- ✅ Verify virtual environment is activated
- ✅ Check if dependencies are installed
- ✅ Verify `.env` file exists
- ✅ Check app structure
- ✅ Start the server automatically if all checks pass

#### Option 3: Manual Start
```bash
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload
```

**Server Options Explained:**
- `--host 0.0.0.0` - Makes the server accessible from other devices on the network
- `--port 1221` - Runs the server on port 1221
- `--reload` - Automatically restarts the server when code changes are detected (development only)

### Step 8: Verify Server is Running

You should see output similar to:

```
INFO:     Will watch for changes in these directories: ['C:\\Users\\oonions\\Documents\\QA projects\\omrs-bridge']
INFO:     Uvicorn running on http://0.0.0.0:1221 (Press CTRL+C to quit)
INFO:     Started reloader process [39208] using WatchFiles
INFO:     Started server process [3664]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

If you see errors, check the [Troubleshooting](#troubleshooting) section.

---

## Docker Setup

If you prefer to run the service in a Docker container:

### Step 1: Ensure Docker is Running

```bash
docker --version
docker-compose --version
```

### Step 2: Configure Environment Variables

Create a `.env` file as described in [Step 5](#step-5-configure-environment-variables) above.

**For Docker, update `DB_HOST` if connecting to an external database:**
- If using Bahmni: `DB_HOST=openmrsdb` (or the actual service name)
- If using local MySQL: `DB_HOST=localhost` or `DB_HOST=host.docker.internal` (Windows/Mac)
- If using remote MySQL: `DB_HOST=<remote_ip_or_hostname>`

### Step 3: Build and Start with Docker Compose

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f openmrs-bridge
```

The `-d` flag runs the container in detached mode (in the background).

### Step 4: Stop Docker Container

```bash
# Stop the container
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker with Bahmni Integration

If you're connecting to an existing Bahmni installation:

1. **Find Bahmni Network:**
   ```bash
   python scripts/setup_bahmni_network.py
   ```

2. **Start with Bahmni configuration:**
   ```bash
   docker-compose -f docker-compose.bahmni.yml up -d
   ```

---

## Verification

### Step 1: Test Health Endpoint

Open your browser or use curl:

```bash
# Browser
http://localhost:1221/health

# Command line (Windows PowerShell)
Invoke-WebRequest -Uri http://localhost:1221/health

# Command line (macOS/Linux)
curl http://localhost:1221/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "OpenMRS Bridge API",
  "version": "1.0.0"
}
```

### Step 2: Access API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:1221/docs
- **ReDoc**: http://localhost:1221/redoc

These interactive documentation pages allow you to test API endpoints directly.

### Step 3: Test API with Authentication

Generate an API key (if you haven't already):
```bash
curl -X POST http://localhost:1221/generate-api-key
```

Test an authenticated endpoint:
```bash
curl -X GET http://localhost:1221/api/v1/system/info \
  -H "Authorization: Bearer omrs_abc123def456ghi789"
```

Replace `omrs_abc123def456ghi789` with one of your actual API keys from the `.env` file.

### Step 4: Verify Database Connection

The service should automatically connect to the database on startup. Check the logs for any connection errors.

If you see database connection errors, verify:
- MySQL server is running
- Database credentials in `.env` are correct
- Network connectivity to the database host
- Database user has proper permissions

---

## Troubleshooting

### Issue: Port 1221 Already in Use

**Solution:**
```bash
# Find what's using the port (Windows)
netstat -ano | findstr :1221

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then update `PORT=8000` in your `.env` file.

### Issue: Database Connection Failed

**Checklist:**
1. ✅ MySQL server is running
2. ✅ Database credentials in `.env` are correct
3. ✅ Database exists (`DB_NAME=openmrs`)
4. ✅ User has permissions to access the database
5. ✅ Network connectivity (if remote database)
6. ✅ Firewall allows connections on port 3306

**Test database connection manually:**
```bash
# Windows
mysql -h localhost -u your_user -p

# Or using Python
python -c "import pymysql; pymysql.connect(host='localhost', user='your_user', password='your_password', database='openmrs')"
```

### Issue: Docker Name Resolution Error (Cannot Resolve `openmrsdb`)

**Error Message:**
```
Name resolution error: Could not resolve hostname 'openmrsdb'
OperationalError: (2003, "Can't connect to MySQL server on 'openmrsdb'")
```

**Understanding the Problem:**

Docker containers use **service names** for DNS resolution. The hostname `openmrsdb` only works if:
1. There's a Docker service/container named `openmrsdb` running
2. Both containers are on the **same Docker network**
3. The service name matches exactly (case-sensitive)

**This error typically occurs when:**
- You're doing a new installation without an existing Bahmni setup
- The Docker network specified doesn't exist
- The database service has a different name than expected
- Containers are on different networks

---

#### Step 1: Diagnose the Problem

**1.1 Check if the database service exists:**
```bash
# List all running containers
docker ps

# Look for MySQL/OpenMRS database containers
docker ps | grep -i mysql
docker ps | grep -i openmrs
```

**1.2 Check Docker networks:**
```bash
# List all Docker networks
docker network ls

# Inspect a specific network (replace with your network name)
docker network inspect bahmni-standard_default
```

**1.3 Check your container's network:**
```bash
# Find your openmrs-bridge container
docker ps | grep openmrs-bridge

# Inspect the container's network configuration
docker inspect <container_id> | grep -A 20 "Networks"
```

**1.4 Test DNS resolution from inside the container:**
```bash
# Get into your openmrs-bridge container
docker exec -it <openmrs-bridge-container-name> bash

# Inside the container, test DNS resolution
ping openmrsdb
nslookup openmrsdb

# Try to connect to MySQL
mysql -h openmrsdb -u your_user -p
```

---

#### Step 2: Identify Your Scenario

**Scenario A: Connecting to Existing Bahmni Installation**

If you have Bahmni already running, you need to connect to its database.

**2.1 Find Bahmni's MySQL service name:**
```bash
# On the Bahmni host, list containers
docker ps

# Look for the MySQL container - note the exact name
# Common names: bahmni-standard-openmrsdb-1, openmrsdb, mysql, etc.
```

**2.2 Find Bahmni's network name:**
```bash
# List networks
docker network ls

# Common Bahmni network names:
# - bahmni-standard_default
# - bahmni_default
# - bahmni_bahmni
# - openmrs_default
```

**2.3 Verify the network exists:**
```bash
# Check if the network exists
docker network inspect bahmni-standard_default

# If you get "Error: No such network", the network doesn't exist
```

---

**Scenario B: Standalone Installation (No Bahmni)**

If you're setting up from scratch without Bahmni, you need your own database setup.

---

#### Step 3: Solutions by Scenario

##### Solution A1: Connect to Existing Bahmni Database

**Step 3.1: Update your `.env` file with the correct service name:**

First, identify the actual MySQL service name from Bahmni:
```bash
# On Bahmni host, find the MySQL container
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

Update `.env`:
```env
# Use the ACTUAL service name from Bahmni, not necessarily "openmrsdb"
DB_HOST=bahmni-standard-openmrsdb-1  # Example - use your actual service name
DB_PORT=3306
DB_NAME=openmrs
DB_USER=your_bahmni_user
DB_PASSWORD=your_bahmni_password
```

**Step 3.2: Update `docker-compose.bahmni.yml` with correct network:**

Find the exact network name:
```bash
docker network ls | grep bahmni
```

Update `docker-compose.bahmni.yml`:
```yaml
networks:
  bahmni-standard_default:  # Use the EXACT network name from docker network ls
    external: true
```

**Step 3.3: Create the network if it doesn't exist (if needed):**

If Bahmni isn't running yet, you may need to start it first:
```bash
# Navigate to Bahmni directory and start it
cd /path/to/bahmni
docker-compose up -d

# Wait for services to start, then verify network exists
docker network ls
```

**Step 3.4: Start the bridge service:**
```bash
# Stop any existing containers
docker-compose -f docker-compose.bahmni.yml down

# Start with the correct configuration
docker-compose -f docker-compose.bahmni.yml up -d

# Check logs
docker-compose -f docker-compose.bahmni.yml logs -f openmrs-bridge
```

**Step 3.5: Verify network connectivity:**
```bash
# Check that both containers are on the same network
docker network inspect bahmni-standard_default

# You should see both:
# - The MySQL container (from Bahmni)
# - The openmrs-bridge container
```

---

##### Solution A2: Use Bahmni Setup Script

The project includes a script to help find Bahmni networks:

```bash
# Run the setup script
python scripts/setup_bahmni_network.py

# This will:
# - Detect running Bahmni services
# - Find Bahmni Docker networks
# - Create environment template
# - Provide connection instructions
```

Follow the script's output to configure your `.env` file.

---

##### Solution B1: Add MySQL Service to Your Docker Compose

For a standalone installation, add MySQL to your `docker-compose.yml`:

**Step 3.1: Update `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  # Add MySQL service
  mysql:
    image: mysql:8.0
    container_name: openmrs-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-password}
      - MYSQL_DATABASE=${DB_NAME:-openmrs}
      - MYSQL_USER=${DB_USER:-openmrs-user}
      - MYSQL_PASSWORD=${DB_PASSWORD:-password}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    networks:
      - openmrs-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  openmrs-bridge:
    build: .
    ports:
      - "1221:1221"
    environment:
      - DB_HOST=mysql  # Use the SERVICE NAME, not "openmrsdb"
      - DB_PORT=${DB_PORT:-3306}
      - DB_NAME=${DB_NAME:-openmrs}
      - DB_USER=${DB_USER:-openmrs-user}
      - DB_PASSWORD=${DB_PASSWORD:-password}
      - API_KEYS=${API_KEYS}
      - SECRET_KEY=${SECRET_KEY}
      - PORT=1221
      - HOST=0.0.0.0
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - openmrs-network

volumes:
  mysql_data:

networks:
  openmrs-network:
    driver: bridge
```

**Step 3.2: Update `.env` file:**
```env
DB_HOST=mysql  # Service name from docker-compose.yml
DB_PORT=3306
DB_NAME=openmrs
DB_USER=openmrs-user
DB_PASSWORD=password
MYSQL_ROOT_PASSWORD=password
```

**Step 3.3: Start services:**
```bash
# Stop any existing containers
docker-compose down

# Start with the new configuration
docker-compose up -d

# Check logs
docker-compose logs -f openmrs-bridge
docker-compose logs -f mysql
```

---

##### Solution B2: Connect to Host Machine's MySQL

If MySQL is running on your host machine (not in Docker):

**Step 3.1: Update `.env` file:**

**Windows:**
```env
DB_HOST=host.docker.internal
DB_PORT=3306
DB_NAME=openmrs
DB_USER=your_user
DB_PASSWORD=your_password
```

**macOS:**
```env
DB_HOST=host.docker.internal
DB_PORT=3306
DB_NAME=openmrs
DB_USER=your_user
DB_PASSWORD=your_password
```

**Linux:**
```env
# Option 1: Use host network mode (in docker-compose.yml)
# Option 2: Use the host's IP address
DB_HOST=172.17.0.1  # Default Docker bridge gateway
# Or find your host IP: ip addr show docker0
```

**Step 3.2: For Linux, you may need to use host network mode:**

Update `docker-compose.yml`:
```yaml
services:
  openmrs-bridge:
    # ... other config ...
    network_mode: "host"  # This allows access to host.docker.internal
```

Or find your Docker bridge IP:
```bash
# Find Docker bridge IP
ip addr show docker0
# Use the inet address (e.g., 172.17.0.1)
```

**Step 3.3: Ensure MySQL allows remote connections:**

Edit MySQL configuration (`/etc/mysql/mysql.conf.d/mysqld.cnf` or similar):
```ini
bind-address = 0.0.0.0  # Allow connections from any IP
```

Restart MySQL:
```bash
sudo systemctl restart mysql
```

**Step 3.4: Start the service:**
```bash
docker-compose up -d
docker-compose logs -f openmrs-bridge
```

---

##### Solution B3: Connect to Remote MySQL Server

If connecting to a MySQL server on another machine:

**Step 3.1: Update `.env` file:**
```env
DB_HOST=192.168.1.100  # Use the actual IP address or hostname
DB_PORT=3306
DB_NAME=openmrs
DB_USER=your_user
DB_PASSWORD=your_password
```

**Step 3.2: Ensure network connectivity:**
```bash
# Test connectivity from Docker container
docker run --rm -it mysql:8.0 mysql -h 192.168.1.100 -u your_user -p
```

**Step 3.3: Update `docker-compose.yml` to remove network restrictions:**

Remove or comment out the `networks:` section if using external network, or ensure the network allows external connections.

**Step 3.4: Start the service:**
```bash
docker-compose up -d
```

---

#### Step 4: Verify the Fix

**4.1 Check container logs:**
```bash
docker-compose logs openmrs-bridge | grep -i "database\|mysql\|error"
```

**4.2 Test connection from inside container:**
```bash
# Get into the container
docker exec -it <openmrs-bridge-container> bash

# Test DNS resolution
ping <your-db-host>
nslookup <your-db-host>

# Test MySQL connection
mysql -h <your-db-host> -u <user> -p
```

**4.3 Test the health endpoint:**
```bash
curl http://localhost:1221/health
```

**4.4 Check if database queries work:**
```bash
curl -X GET http://localhost:1221/api/v1/system/info \
  -H "Authorization: Bearer <your-api-key>"
```

---

#### Step 5: Common Network Issues and Fixes

**Issue: Network doesn't exist**
```bash
# Error: network bahmni-standard_default not found
# Solution: Create the network or use the correct name
docker network create bahmni-standard_default
# OR update docker-compose.yml with the correct network name
```

**Issue: Containers on different networks**
```bash
# Check which network each container is on
docker inspect <container-id> | grep NetworkMode

# Solution: Ensure both containers use the same network in docker-compose.yml
```

**Issue: Service name mismatch**
```bash
# The service name in DB_HOST must match the service name in docker-compose.yml
# Check service names:
docker-compose config | grep -A 5 "services:"

# Update .env to match the actual service name
```

**Issue: Network is external but doesn't exist**
```bash
# If using external: true, the network must exist BEFORE starting containers
# Check if it exists:
docker network ls | grep bahmni

# If it doesn't exist, either:
# 1. Start Bahmni first to create the network
# 2. Create the network manually: docker network create <network-name>
# 3. Remove external: true and let Docker create it
```

---

#### Quick Diagnostic Checklist

Use this checklist to systematically diagnose the issue:

- [ ] **Is the database service running?**
  ```bash
  docker ps | grep -i mysql
  ```

- [ ] **What is the exact service name?**
  ```bash
  docker ps --format "{{.Names}}"
  ```

- [ ] **Does the network exist?**
  ```bash
  docker network ls
  ```

- [ ] **Are both containers on the same network?**
  ```bash
  docker network inspect <network-name>
  ```

- [ ] **Can the container resolve the hostname?**
  ```bash
  docker exec -it <container> ping <db-hostname>
  ```

- [ ] **Is DB_HOST in .env correct?**
  - Must match the service name exactly (case-sensitive)
  - Not `openmrsdb` unless that's the actual service name

- [ ] **Is the network configuration correct in docker-compose.yml?**
  - Network name matches the actual network
  - `external: true` only if network exists externally

---

#### Summary: Quick Fix Reference

| Scenario | DB_HOST Value | Network Configuration |
|----------|--------------|----------------------|
| **Bahmni Integration** | Actual Bahmni MySQL service name | `bahmni-standard_default` (external) |
| **Standalone with MySQL container** | `mysql` (service name) | Create shared network |
| **Host MySQL (Windows/Mac)** | `host.docker.internal` | Default bridge network |
| **Host MySQL (Linux)** | `172.17.0.1` or host IP | Default bridge or host network |
| **Remote MySQL** | IP address or hostname | Default bridge network |

**Remember:** The `DB_HOST` value must be the **Docker service name** when both containers are in Docker, or an **IP/hostname** when connecting to external databases.

### Issue: Module Not Found Errors

**Solution:**
```bash
# Ensure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt

# If still failing, recreate virtual environment
deactivate
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Issue: API Key Authentication Failed

**Checklist:**
1. ✅ API key format is correct: `omrs_<32_chars>`
2. ✅ API key is in `API_KEYS` environment variable (comma-separated)
3. ✅ Using `Authorization: Bearer <key>` header format
4. ✅ No extra spaces in API key
5. ✅ `.env` file is in the project root directory

**Generate a new API key:**
```bash
curl -X POST http://localhost:1221/generate-api-key
```

### Issue: Virtual Environment Not Activating

**Windows PowerShell:**
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**Alternative (Windows):**
```cmd
venv\Scripts\activate.bat
```

### Issue: Python Version Too Old

**Solution:**
- Download and install Python 3.11 or higher from [python.org](https://www.python.org/downloads/)
- Verify installation: `python --version`
- Recreate virtual environment with new Python version

### Issue: Docker Container Won't Start

**Checklist:**
1. ✅ Docker Desktop is running
2. ✅ `.env` file exists and is configured
3. ✅ Port 1221 is not already in use
4. ✅ Database host is accessible from Docker container

**View Docker logs:**
```bash
docker-compose logs -f openmrs-bridge
```

**Rebuild Docker image:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Next Steps

Once your service is running:

1. **Explore the API Documentation**: Visit http://localhost:1221/docs
2. **Test Endpoints**: Use the interactive Swagger UI to test API calls
3. **Review API Endpoints**: Check available endpoints in the documentation
4. **Set Up Monitoring**: Configure health checks and logging
5. **Production Deployment**: Review `README.md` for production deployment instructions

---

## Quick Reference

### Common Commands

```bash
# Start development server
python scripts/start_dev.py

# Start manually
uvicorn app.main:app --host 0.0.0.0 --port 1221 --reload

# Start with Docker
docker-compose up -d

# View logs (Docker)
docker-compose logs -f openmrs-bridge

# Stop server
# Press Ctrl+C in the terminal

# Stop Docker
docker-compose down

# Generate API key
curl -X POST http://localhost:1221/generate-api-key

# Health check
curl http://localhost:1221/health
```

### Important URLs

- **API Base**: http://localhost:1221/api/v1
- **API Docs (Swagger)**: http://localhost:1221/docs
- **API Docs (ReDoc)**: http://localhost:1221/redoc
- **Health Check**: http://localhost:1221/health

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the main `README.md` file for additional information
2. Review error messages in the terminal/logs
3. Verify all prerequisites are met
4. Check the [Troubleshooting](#troubleshooting) section above
5. Review API documentation at `/docs` endpoint

---

**Setup Complete!** 🎉

Your OpenMRS Bridge API service should now be running and ready to use.

