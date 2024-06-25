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
