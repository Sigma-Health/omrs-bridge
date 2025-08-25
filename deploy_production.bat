@echo off
setlocal enabledelayedexpansion

echo 🚀 OpenMRS Bridge API - Production Deployment
echo ==============================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    exit /b 1
)

echo ✅ Docker is available

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed or not in PATH
    exit /b 1
)

echo ✅ Docker Compose is available

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found
    if exist "env.production" (
        echo ✅ Copying production environment template
        copy env.production .env
        echo ⚠️  Please edit .env file with your production values before continuing
        echo ⚠️  Press any key when ready to continue...
        pause >nul
    ) else (
        echo ❌ No environment file found. Please create .env file with required variables
        exit /b 1
    )
)

echo ✅ Environment file found

REM Create necessary directories
echo ✅ Creating necessary directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "ssl" mkdir ssl

REM Check if Bahmni network exists
echo ✅ Checking Bahmni network
docker network ls | findstr "bahmni_default" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Bahmni network not found. Creating it...
    docker network create bahmni_default
)

REM Build the application
echo ✅ Building Docker image
docker-compose -f docker-compose.prod.yml build
if errorlevel 1 (
    echo ❌ Build failed
    exit /b 1
)

REM Stop existing containers
echo ✅ Stopping existing containers
docker-compose -f docker-compose.prod.yml down

REM Start the application
echo ✅ Starting production services
docker-compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    exit /b 1
)

REM Wait for application to start
echo ✅ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if application is running
echo ✅ Checking application health
curl -f http://localhost:1221/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Application health check failed
    echo ✅ Checking logs...
    docker-compose -f docker-compose.prod.yml logs openmrs-bridge
    exit /b 1
)

echo.
echo 🎉 Deployment completed successfully!
echo ======================================
echo Application URL: http://localhost:1221
echo Health Check: http://localhost:1221/health
echo API Documentation: http://localhost:1221/docs
echo.
echo Useful commands:
echo   View logs: docker-compose -f docker-compose.prod.yml logs -f
echo   Stop services: docker-compose -f docker-compose.prod.yml down
echo   Restart services: docker-compose -f docker-compose.prod.yml restart
echo   Update application: deploy_production.bat

pause 