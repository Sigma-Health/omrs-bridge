#!/bin/bash

# Production Deployment Script for OpenMRS Bridge API
set -e

echo "🚀 OpenMRS Bridge API - Production Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running"
    exit 1
fi

print_status "Docker is available"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

print_status "Docker Compose is available"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f "env.production" ]; then
        print_status "Copying production environment template"
        cp env.production .env
        print_warning "Please edit .env file with your production values before continuing"
        print_warning "Press Enter when ready to continue..."
        read
    else
        print_error "No environment file found. Please create .env file with required variables"
        exit 1
    fi
fi

# Validate required environment variables
print_status "Validating environment variables"

required_vars=("DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD" "API_KEYS" "SECRET_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables: ${missing_vars[*]}"
    print_warning "Please update your .env file"
    exit 1
fi

print_status "Environment variables validated"

# Create necessary directories
print_status "Creating necessary directories"
mkdir -p logs data ssl

# Check if Bahmni network exists
print_status "Checking Bahmni network"
if ! docker network ls | grep -q "bahmni_default"; then
    print_warning "Bahmni network not found. Creating it..."
    docker network create bahmni_default
fi

# Build the application
print_status "Building Docker image"
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
print_status "Stopping existing containers"
docker-compose -f docker-compose.prod.yml down

# Start the application
print_status "Starting production services"
docker-compose -f docker-compose.prod.yml up -d

# Wait for application to start
print_status "Waiting for application to start..."
sleep 10

# Check if application is running
print_status "Checking application health"
if curl -f http://localhost:1221/health > /dev/null 2>&1; then
    print_status "Application is healthy and running"
else
    print_error "Application health check failed"
    print_status "Checking logs..."
    docker-compose -f docker-compose.prod.yml logs openmrs-bridge
    exit 1
fi

# Show deployment information
echo ""
echo "🎉 Deployment completed successfully!"
echo "======================================"
echo "Application URL: http://localhost:1221"
echo "Health Check: http://localhost:1221/health"
echo "API Documentation: http://localhost:1221/docs"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "  Update application: ./deploy_production.sh" 