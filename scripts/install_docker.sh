#!/bin/bash
# Install Docker on Ubuntu 22.04 (Master VM)

echo "========================================="
echo "Installing Docker"
echo "========================================="

# Update package index
echo "→ Updating package index..."
sudo apt-get update

# Install prerequisites
echo "→ Installing prerequisites..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
echo "→ Adding Docker GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "→ Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt-get update

# Install Docker
echo "→ Installing Docker Engine..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group (avoid sudo for docker commands)
echo "→ Adding user to docker group..."
sudo usermod -aG docker $USER

# Start Docker
echo "→ Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
echo ""
echo "→ Verifying Docker installation..."
sudo docker run hello-world

echo ""
echo "========================================="
echo "✓ Docker Installation Complete!"
echo "========================================="
echo "**IMPORTANT**: Log out and log back in for group changes to take effect"
echo "Then you can run docker commands without sudo"
echo "========================================="
