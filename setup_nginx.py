#!/usr/bin/env python3

import os
import subprocess

# Function to run a shell command
def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        exit(1)

# Create the /etc/ssl/nginx/ directory with sudo
ssl_dir = '/etc/ssl/nginx'
if not os.path.exists(ssl_dir):
    print(f"Creating directory: {ssl_dir}")
    run_command(f'sudo mkdir -p {ssl_dir}')
else:
    print(f"Directory already exists: {ssl_dir}")

# Paths to the certificate and key files in the current directory
current_dir = os.getcwd()
cert_file = os.path.join(current_dir, 'nginx-repo.crt')
key_file = os.path.join(current_dir, 'nginx-repo.key')

# Check if the files exist
if not os.path.isfile(cert_file):
    print(f"Certificate file not found: {cert_file}")
    exit(1)

if not os.path.isfile(key_file):
    print(f"Key file not found: {key_file}")
    exit(1)

# Copy nginx-repo.crt and nginx-repo.key files to the /etc/ssl/nginx/ directory with sudo
print(f"Copying {cert_file} to {ssl_dir}")
run_command(f'sudo cp {cert_file} {ssl_dir}')

print(f"Copying {key_file} to {ssl_dir}")
run_command(f'sudo cp {key_file} {ssl_dir}')

# Remove any previous NGINX repository and apt configuration files
print("Removing old NGINX repository and configuration files")
run_command('sudo rm -f /etc/apt/sources.list.d/nginx*.list')
run_command('sudo rm -f /etc/apt/sources.list.d/*app-protect*.list')
run_command('sudo rm -f /etc/apt/apt.conf.d/90pkgs-nginx')

# Remove App Armor (conflicts with app protect install)
print("Removing & Disabling App Armor")
run_command('sudo aa-teardown')
run_command('sudo systemctl stop apparmor')
run_command('sudo systemctl disable apparmor')
print("App Armor Disabled...")

# Install prerequisite packages
print("Installing prerequisite packages")
run_command('sudo apt-get update && sudo apt-get install -y apt-transport-https lsb-release ca-certificates gnupg2 ubuntu-keyring curl')

# Download and add the NGINX signing key using curl
print("Downloading and adding the NGINX signing key")
nginx_key_url = 'https://cs.nginx.com/static/keys/nginx_signing.key'
keyring_path = '/usr/share/keyrings/nginx-archive-keyring.gpg'
run_command(f'curl -s {nginx_key_url} | gpg --dearmor | sudo tee {keyring_path} >/dev/null')

# Download the apt configuration to /etc/apt/apt.conf.d using curl
print("Downloading the apt configuration")
config_url = 'https://cs.nginx.com/static/files/90pkgs-nginx'
config_path = '/etc/apt/apt.conf.d/90pkgs-nginx'
run_command(f'sudo curl -s -o {config_path} {config_url}')

# Verify that the downloaded key contains the proper fingerprint
print("Verifying the downloaded key")
fingerprint = "573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62"
command = f'gpg --dry-run --quiet --no-keyring --import --import-options import-show {keyring_path}'
result = subprocess.run(command, shell=True, capture_output=True, text=True)
if fingerprint in result.stdout:
    print(f"Key verification successful. Fingerprint: {fingerprint}")
else:
    print(f"Key verification failed. Removing {keyring_path}")
    run_command(f'sudo rm {keyring_path}')
    exit(1)

# Add the NGINX Plus repository
print("Adding the NGINX Plus repository")
run_command(f'printf "deb [signed-by={keyring_path}] https://pkgs.nginx.com/plus/ubuntu `lsb_release -cs` nginx-plus\\n" | sudo tee /etc/apt/sources.list.d/nginx-plus.list')

# Add the NGINX App Protect WAF v5 repository
print("Adding the NGINX App Protect WAF v5 repository")
run_command(f'printf "deb [signed-by={keyring_path}] https://pkgs.nginx.com/app-protect-x-plus/ubuntu `lsb_release -cs` nginx-plus\\n" | sudo tee /etc/apt/sources.list.d/nginx-app-protect.list')

# Install the NGINX App Protect WAF v5 package
print("Updating package list and installing NGINX App Protect WAF v5")
run_command('sudo apt-get update')
run_command('sudo apt-get install -y app-protect-module-plus')

print("Starting NGINX+ with App Protect.")
run_command('sudo systemctl start nginx')


# Function to run a shell command and return its output
def run_command(command, capture_output=False):
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            return result.stdout.strip()
        else:
            subprocess.check_call(command, shell=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        exit(1)

# Function to return app protect version
def get_app_protect_version():
    try:
        # Query the package management system for the installed version of app-protect-module-plus
        version_output = run_command('dpkg -l | grep app-protect-module-plus', capture_output=True)
        if version_output:
            version = version_output.split()[2]
            return version
        else:
            return "App Protect version not found"
    except Exception as e:
        print(f"Failed to get App Protect version: {e}")
        return "App Protect version not found"

# Display versions and status
app_protect_version = get_app_protect_version()


print("\n--- NGINX App Protect Version Information ---")
print(f"App Protect Version: {app_protect_version}")

# Docker and Docker Compose installation script
docker_script = """
#!/bin/bash

# Function to check the latest Docker Compose release
latest_compose_release_url="https://github.com/docker/compose/releases/latest"

echo "Docker Compose Installation Script"
echo "=================================="
echo "You can find the latest Docker Compose release version here: $latest_compose_release_url"
echo "Please enter the Docker Compose version you want to install - numbers only (e.g., 2.12.2):"
read -p "Version: " compose_version

if [ -z "$compose_version" ]; then
  echo "No version entered. Exiting."
  exit 1
fi

# Update the system
echo "Updating the system..."
sudo apt update && sudo apt upgrade -y

#WAF Services Configuration
#Create directories
sudo mkdir -p /opt/app_protect/config /opt/app_protect/bd_config
#Set ownership
sudo chown -R 101:101 /opt/app_protect/


# Copying certs for NGINX private registry
sudo mkdir -p /etc/docker/certs.d/private-registry.nginx.com
sudo cp nginx-repo.crt /etc/docker/certs.d/private-registry.nginx.com/client.cert
sudo cp nginx-repo.key /etc/docker/certs.d/private-registry.nginx.com/client.key

# Uninstall old versions of Docker
echo "Removing old Docker versions..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc

# Install required packages
echo "Installing required packages..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
echo "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add the Docker repository
echo "Adding Docker repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update the package database
echo "Updating package database..."
sudo apt update

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Add user to Docker group
echo "Adding current user to Docker group..."
sudo usermod -aG docker $USER

# Remove existing docker-compose file if present
if [ -f /usr/local/bin/docker-compose ]; then
    echo "Removing old Docker Compose..."
    sudo rm /usr/local/bin/docker-compose
fi

# Download and install Docker Compose
echo "Installing Docker Compose version $compose_version..."
sudo curl -L "https://github.com/docker/compose/releases/download/v$compose_version/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make Docker Compose executable
echo "Making Docker Compose executable..."
sudo chmod +x /usr/local/bin/docker-compose

# Verify the installation
echo "Verifying Docker Compose installation..."
docker-compose --version

# Enable Docker to start on boot
echo "Enabling Docker to start on boot..."
sudo systemctl enable docker

# Output versions
echo "Installed Docker version:"
docker --version
echo "Installed Docker Compose version:"
docker-compose --version

echo "Installation completed. Please log out and back in or run 'newgrp docker' to use Docker without sudo."
"""

# Write the Docker installation script to a file
docker_script_path = os.path.join(current_dir, 'install_docker.sh')
with open(docker_script_path, 'w') as f:
    f.write(docker_script)

# Make the script executable
run_command(f'chmod +x {docker_script_path}')

# Execute the Docker installation script
print("Executing Docker installation script...")
run_command(f'sudo {docker_script_path}')

# Appending the Docker Compose YAML content
docker_compose_content = """
services:
  waf-enforcer:
    container_name: waf-enforcer
    image: private-registry.nginx.com/nap/waf-enforcer:5.2.0
    environment:
      - ENFORCER_PORT=50000
    ports:
      - "50000:50000"
    volumes:
      - /opt/app_protect/bd_config:/opt/app_protect/bd_config
    networks:
      - waf_network
    restart: always

  waf-config-mgr:
    container_name: waf-config-mgr
    image: private-registry.nginx.com/nap/waf-config-mgr:5.2.0
    volumes:
      - /opt/app_protect/bd_config:/opt/app_protect/bd_config
      - /opt/app_protect/config:/opt/app_protect/config
      - /etc/app_protect/conf:/etc/app_protect/conf
    restart: always
    network_mode: none
    depends_on:
      waf-enforcer:
        condition: service_started

networks:
  waf_network:
    driver: bridge
"""

# Write Docker Compose content to docker-compose.yml
with open('docker-compose.yml', 'w') as file:
    file.write(docker_compose_content)

# Run Docker Compose
import subprocess

try:
    subprocess.run(["sudo", "docker-compose", "up", "-d"], check=True)
    print("Docker Compose ran successfully.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred while running Docker Compose: {e}")