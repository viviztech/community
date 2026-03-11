#!/bin/bash
echo "🚀 Starting permanent disk & swap fix..."

# Stop Docker
echo "Stopping Docker..."
sudo systemctl stop docker

# Move Docker data to large disk
echo "Moving Docker to /mnt/newvolume/docker..."
sudo mkdir -p /mnt/newvolume/docker
sudo mv /var/lib/docker /mnt/newvolume/docker 2>/dev/null
sudo ln -s /mnt/newvolume/docker /var/lib/docker

# Start Docker
echo "Starting Docker..."
sudo systemctl start docker

# Create permanent 4G swap on large disk
echo "Setting up 4G swap on /mnt/newvolume..."
sudo swapoff -a
sudo rm -f /swapfile
sudo fallocate -l 4G /mnt/newvolume/swapfile
sudo chmod 600 /mnt/newvolume/swapfile
sudo mkswap /mnt/newvolume/swapfile
sudo swapon /mnt/newvolume/swapfile

# Make swap permanent
grep -q "/mnt/newvolume/swapfile" /etc/fstab || echo "/mnt/newvolume/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab

# Redirect /tmp to large disk
echo "Redirecting /tmp to /mnt/newvolume/tmp..."
sudo rm -rf /tmp
sudo mkdir -p /mnt/newvolume/tmp
sudo ln -s /mnt/newvolume/tmp /tmp

# Redirect npm cache to large disk
echo "Redirecting npm cache to /mnt/newvolume/npm-cache..."
mkdir -p /mnt/newvolume/npm-cache
npm config set cache /mnt/newvolume/npm-cache --global

# Optional: move global node_modules
echo "Moving global node_modules to large disk..."
sudo mkdir -p /mnt/newvolume/node_modules
sudo mv /usr/lib/node_modules /mnt/newvolume/node_modules 2>/dev/null
sudo ln -s /mnt/newvolume/node_modules /usr/lib/node_modules

echo "✅ Permanent disk, swap, npm, and temp fix completed!"
echo "You can now run npm install, build, and PM2 without errors."
