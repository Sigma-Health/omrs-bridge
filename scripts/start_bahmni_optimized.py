#!/usr/bin/env python3
"""
Startup script for OpenMRS Bridge with Bahmni integration (Optimized)
"""

import subprocess
import sys
import os
import time
import requests
import json
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None


def check_docker():
    """Check if Docker is running"""
    print("🔍 Checking Docker...")
    result = run_command("docker version")
    if not result or result.returncode != 0:
        print("❌ Docker is not running or not accessible")
        return False
    print("✅ Docker is running")
    return True


def check_bahmni_network():
    """Check if Bahmni network exists"""
    print("🔍 Checking Bahmni network...")
    result = run_command("docker network ls --format 'table {{.Name}}' | grep bahmni")
    if not result or result.returncode != 0:
        print("❌ Bahmni network not found")
        print("Available networks:")
        run_command("docker network ls", capture_output=False)
        return False
    
    networks = result.stdout.strip().split('\n')
    if networks:
        print(f"✅ Found Bahmni networks: {', '.join(networks)}")
        return True
    else:
        print("❌ No Bahmni networks found")
        return False


def check_bahmni_services():
    """Check if Bahmni services are running"""
    print("🔍 Checking Bahmni services...")
    result = run_command("docker ps --format 'table {{.Names}}\t{{.Image}}' | grep -i bahmni")
    if not result or result.returncode != 0:
        print("⚠️  No Bahmni services found running")
        return False
    
    services = result.stdout.strip().split('\n')
    if services:
        print(f"✅ Found {len(services)} Bahmni services running")
        for service in services:
            print(f"   - {service}")
        return True
    else:
        print("⚠️  No Bahmni services found")
        return False


def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create .env file with your Bahmni database credentials")
        return False
    
    # Check required environment variables
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration looks good")
    return True


def build_optimized_image():
    """Build the optimized Docker image"""
    print("🔨 Building optimized Docker image...")
    result = run_command("docker build -f Dockerfile.optimized -t openmrs-bridge-bahmni:latest .")
    if not result or result.returncode != 0:
        print("❌ Failed to build Docker image")
        return False
    print("✅ Docker image built successfully")
    return True


def start_services():
    """Start the Bahmni-optimized services"""
    print("🚀 Starting OpenMRS Bridge with Bahmni integration...")
    
    # Start core services first
    result = run_command("docker-compose -f docker-compose.bahmni.yml up -d openmrs-bridge-bahmni redis-cache")
    if not result or result.returncode != 0:
        print("❌ Failed to start core services")
        return False
    
    print("✅ Core services started")
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(30)
    
    # Check if services are healthy
    if not check_service_health():
        print("❌ Services are not healthy")
        return False
    
    # Start optional services
    print("🚀 Starting optional services (nginx, monitoring)...")
    result = run_command("docker-compose -f docker-compose.bahmni.yml up -d nginx-proxy prometheus-bahmni grafana-bahmni")
    if result and result.returncode == 0:
        print("✅ Optional services started")
    else:
        print("⚠️  Some optional services failed to start")
    
    return True


def check_service_health():
    """Check if services are healthy"""
    print("🔍 Checking service health...")
    
    # Check OpenMRS Bridge health
    try:
        response = requests.get("http://localhost:1221/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ OpenMRS Bridge is healthy: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ OpenMRS Bridge health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenMRS Bridge health check error: {e}")
        return False
    
    # Check Redis health
    try:
        response = requests.get("http://localhost:6379", timeout=5)
        print("✅ Redis is accessible")
    except:
        print("⚠️  Redis health check failed (this is normal if Redis doesn't expose HTTP)")
    
    return True


def show_service_info():
    """Show information about running services"""
    print("\n" + "=" * 60)
    print("🎉 OpenMRS Bridge with Bahmni Integration Started!")
    print("=" * 60)
    
    print("\n📊 Service Information:")
    print("  • OpenMRS Bridge API: http://localhost:1221")
    print("  • API Documentation: http://localhost:1221/docs")
    print("  • Health Check: http://localhost:1221/health")
    print("  • Performance Metrics: http://localhost:1221/performance")
    print("  • Database Stats: http://localhost:1221/stats")
    
    print("\n🌐 Optional Services:")
    print("  • Nginx Proxy: http://localhost:8090")
    print("  • Prometheus: http://localhost:9099")
    print("  • Grafana: http://localhost:3111 (admin/admin)")
    print("  • Redis Cache: localhost:6379")
    
    print("\n🔧 Management Commands:")
    print("  • View logs: docker-compose -f docker-compose.bahmni.yml logs -f")
    print("  • Stop services: docker-compose -f docker-compose.bahmni.yml down")
    print("  • Restart services: docker-compose -f docker-compose.bahmni.yml restart")
    print("  • Check status: docker-compose -f docker-compose.bahmni.yml ps")
    
    print("\n📝 API Usage Examples:")
    print("  • List orders: curl -H 'Authorization: Bearer your_api_key' http://localhost:1221/api/v1/orders/")
    print("  • List observations: curl -H 'Authorization: Bearer your_api_key' http://localhost:1221/api/v1/observations/")
    print("  • Get health: curl http://localhost:1221/health")
    
    print("\n💡 Tips:")
    print("  • Make sure your .env file has correct Bahmni database credentials")
    print("  • The API uses UUID-based endpoints for better performance")
    print("  • Check /performance endpoint for real-time metrics")
    print("  • Monitor logs for any connection issues")


def main():
    """Main function"""
    print("🚀 OpenMRS Bridge - Bahmni Integration (Optimized)")
    print("=" * 60)
    
    # Check prerequisites
    if not check_docker():
        sys.exit(1)
    
    if not check_bahmni_network():
        print("⚠️  Bahmni network not found, but continuing...")
    
    if not check_bahmni_services():
        print("⚠️  No Bahmni services found, but continuing...")
    
    if not check_environment():
        print("❌ Environment configuration issues")
        print("Please create a .env file with your Bahmni database credentials")
        sys.exit(1)
    
    # Build and start services
    if not build_optimized_image():
        sys.exit(1)
    
    if not start_services():
        sys.exit(1)
    
    # Show service information
    show_service_info()


if __name__ == "__main__":
    main() 