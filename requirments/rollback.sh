#!/bin/bash

# Check if original settings file exists
if [ ! -f original_network_settings.netconf ]; then
    echo "Error: Original settings file not found. Cannot roll back."
    exit 1
fi

echo "Rolling back to original network settings..."

# Read and apply original values
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ $line =~ ^#.*$ || -z $line ]] && continue
    
    # Parse and apply setting
    setting=$(echo "$line" | cut -d= -f1)
    value=$(echo "$line" | cut -d= -f2-)
    
    if [ -n "$setting" ] && [ -n "$value" ]; then
        echo "Restoring $setting to $value"
        sysctl -w "$setting"="$value"
    fi
done < original_network_settings.netconf

# Remove custom sysctl config file
if [ -f /etc/sysctl.d/60-udp-performance.conf ]; then
    echo "Removing custom sysctl configuration file..."
    rm /etc/sysctl.d/60-udp-performance.conf
    
    # Apply system defaults
    sysctl --system
fi

# Revert any user limits in limits.conf
if grep -q "nofile" /etc/security/limits.conf; then
    echo "Reverting file descriptor limits in limits.conf..."
    sed -i '/nofile/d' /etc/security/limits.conf
fi

# Revert firewall rules if needed
if command -v ufw >/dev/null 2>&1; then
    ufw status | grep -q "50000:50002/udp" && {
        echo "Removing UDP firewall rules for ports 50000-50002..."
        ufw delete allow 50000:50002/udp
    }
fi

echo "Rollback completed. System has been restored to original settings."
echo "Original settings file 'original_network_settings.netconf' preserved for reference."