#!/usr/bin/env python3
"""
Setup script to help connect the OpenMRS Bridge to Bahmni network
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None


def find_bahmni_networks():
    """Find all Docker networks that might be Bahmni-related"""
    print("🔍 Searching for Bahmni networks...")
    
    # Get all Docker networks
    result = run_command("docker network ls --format 'table {{.Name}}\t{{.Driver}}\t{{.Scope}}'")
    if not result or result.returncode != 0:
        print("❌ Failed to list Docker networks")
        return []
    
    networks = []
    lines = result.stdout.strip().split('\n')[1:]  # Skip header
    
    for line in lines:
        if line.strip():
            parts = line.split('\t')
            if len(parts) >= 2:
                name, driver, scope = parts[0], parts[1], parts[2] if len(parts) > 2 else 'local'
                if 'bahmni' in name.lower() or 'openmrs' in name.lower():
                    networks.append((name, driver, scope))
    
    return networks


def find_bahmni_services():
    """Find running Bahmni services"""
    print("🔍 Searching for Bahmni services...")
    
    # Get all running containers
    result = run_command("docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'")
    if not result or result.returncode != 0:
        print("❌ Failed to list Docker containers")
        return []
    
    services = []
    lines = result.stdout.strip().split('\n')[1:]  # Skip header
    
    for line in lines:
        if line.strip():
            parts = line.split('\t')
            if len(parts) >= 2:
                name, image = parts[0], parts[1]
                if 'bahmni' in name.lower() or 'openmrs' in name.lower() or 'mysql' in image.lower():
                    services.append((name, image))
    
    return services


def get_network_details(network_name):
    """Get detailed information about a network"""
    print(f"🔍 Getting details for network: {network_name}")
    
    result = run_command(f"docker network inspect {network_name}")
    if not result or result.returncode != 0:
        print(f"❌ Failed to inspect network {network_name}")
        return None
    
    return result.stdout


def create_env_template():
    """Create environment template for Bahmni connection"""
    env_content = """# Bahmni Database Configuration
# Update these values based on your Bahmni setup

# Database host (usually the MySQL service name in Bahmni)
DB_HOST=openmrsdb

# Database port (usually 3306)
DB_PORT=3306

# Database name (usually 'openmrs')
DB_NAME=openmrs

# Database user (check your Bahmni configuration)
DB_USER=root

# Database password (check your Bahmni configuration)
DB_PASSWORD=your_bahmni_mysql_password

# API Keys (comma-separated)
API_KEYS=omrs_abc123def456ghi789,omrs_xyz789uvw456rst123

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Application settings
PORT=1221
HOST=0.0.0.0
DEBUG=true
"""
    
    with open('.env.bahmni', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.bahmni template")


def main():
    """Main function"""
    print("🚀 OpenMRS Bridge - Bahmni Network Setup")
    print("=" * 50)
    
    # Check if Docker is running
    result = run_command("docker version")
    if not result or result.returncode != 0:
        print("❌ Docker is not running or not accessible")
        print("Please start Docker and try again")
        return
    
    print("✅ Docker is running")
    
    # Find Bahmni networks
    networks = find_bahmni_networks()
    
    if not networks:
        print("❌ No Bahmni networks found")
        print("\nPossible reasons:")
        print("1. Bahmni is not running")
        print("2. Bahmni uses a different network naming convention")
        print("3. You need to start Bahmni first")
        
        # Show all networks for reference
        print("\nAll available networks:")
        result = run_command("docker network ls")
        if result:
            print(result.stdout)
        
        return
    
    print(f"\n✅ Found {len(networks)} potential Bahmni networks:")
    for i, (name, driver, scope) in enumerate(networks, 1):
        print(f"{i}. {name} ({driver}, {scope})")
    
    # Find Bahmni services
    services = find_bahmni_services()
    
    if services:
        print(f"\n✅ Found {len(services)} potential Bahmni services:")
        for name, image in services:
            print(f"  - {name} ({image})")
    
    # Create environment template
    print("\n📝 Creating environment template...")
    create_env_template()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Copy .env.bahmni to .env and update with your Bahmni credentials")
    print("2. Run: docker-compose -f docker-compose.bahmni.yml up -d")
    print("3. Check logs: docker-compose -f docker-compose.bahmni.yml logs -f")
    
    if networks:
        print(f"\n💡 Recommended network: {networks[0][0]}")
        print("If this doesn't work, try the other networks listed above")


if __name__ == "__main__":
    main() 