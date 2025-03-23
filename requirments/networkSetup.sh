#!/bin/bash

# Save the original settings for rollback
echo "# Original network settings - $(date)" > original_network_settings.netconf
echo "net.core.rmem_max=$(cat /proc/sys/net/core/rmem_max)" >> original_network_settings.netconf
echo "net.core.wmem_max=$(cat /proc/sys/net/core/wmem_max)" >> original_network_settings.netconf
echo "net.core.rmem_default=$(cat /proc/sys/net/core/rmem_default)" >> original_network_settings.netconf
echo "net.core.wmem_default=$(cat /proc/sys/net/core/wmem_default)" >> original_network_settings.netconf
echo "net.ipv4.udp_mem=$(cat /proc/sys/net/ipv4/udp_mem)" >> original_network_settings.netconf
echo "net.ipv4.udp_rmem_min=$(cat /proc/sys/net/ipv4/udp_rmem_min)" >> original_network_settings.netconf
echo "net.ipv4.udp_wmem_min=$(cat /proc/sys/net/ipv4/udp_wmem_min)" >> original_network_settings.netconf
echo "fs.file-max=$(cat /proc/sys/fs/file-max)" >> original_network_settings.netconf

# Socket buffer settings
echo "Increasing socket buffer limits..."
sysctl -w net.core.rmem_max=10485760
sysctl -w net.core.wmem_max=10485760
sysctl -w net.core.rmem_default=10485760
sysctl -w net.core.wmem_default=10485760

# UDP specific settings
echo "Configuring UDP memory settings..."
sysctl -w net.ipv4.udp_mem="10240 87380 12582912"
sysctl -w net.ipv4.udp_rmem_min=10240
sysctl -w net.ipv4.udp_wmem_min=10240

# File descriptor settings
echo "Increasing file descriptor limits..."
sysctl -w fs.file-max=2097152

# Update limits.conf for user limits
if ! grep -q "nofile" /etc/security/limits.conf; then
    echo "Setting user file descriptor limits..."
    echo "* soft nofile 1048576" >> /etc/security/limits.conf
    echo "* hard nofile 1048576" >> /etc/security/limits.conf
fi

# Create sysctl config file for persistence
echo "Creating persistent configuration file..."
cat > /etc/sysctl.d/60-udp-performance.conf << EOL
# UDP Communication Performance Settings
net.core.rmem_max = 10485760
net.core.wmem_max = 10485760
net.core.rmem_default = 10485760
net.core.wmem_default = 10485760
net.ipv4.udp_mem = 10240 87380 12582912
net.ipv4.udp_rmem_min = 10240
net.ipv4.udp_wmem_min = 10240
fs.file-max = 2097152
EOL

# Apply all settings
echo "Applying all settings..."
sysctl -p /etc/sysctl.d/60-udp-performance.conf

# Check if required ports are available
echo "Checking if ports 50000, 50001, and 50002 are available..."
for port in 50000 50001 50002; do
    if ss -lun | grep -q ":$port "; then
        echo "Warning: Port $port is already in use!"
    else
        echo "Port $port is available."
    fi
done

# Enable UDP broadcast if needed
echo "Checking firewall rules for UDP broadcast..."
if command -v ufw >/dev/null 2>&1; then
    ufw status | grep -q "Status: active" && {
        echo "Enabling UDP on ports 50000-50002..."
        ufw allow 50000:50002/udp
    }
fi

echo "Setup completed. The system is now configured for high-performance UDP communication."
echo "To revert changes, run the rollback.sh script."