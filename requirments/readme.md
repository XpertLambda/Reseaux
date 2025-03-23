# Requirements for UDP Python-C Communication System

## System Setup Instructions

1. Run the setup script to configure your system for optimal UDP performance:
   ```
   sudo ./networkSetup.sh
   ```

2. If you need to restore your system to original settings:
   ```
   sudo ./rollback.sh
   ```

## Network Performance Tuning

If experiencing UDP packet loss:

1. Increase the network interface queue length:
   ```
   sudo ifconfig <interface> txqueuelen 10000
   ```
   Replace `<interface>` with your network interface

2. Consider enabling jumbo frames if your network hardware supports it:
   ```
   sudo ifconfig <interface> mtu 9000
   ```

## Application Configuration

1. The system uses the following ports by default:
   - 50000: Python port
   - 50001, 50002: C application ports
   
   Ensure these ports are not used by other applications

2. Verify broadcast permissions:
   ```
   sudo iptables -A INPUT -p udp --dport 50000:50002 -j ACCEPT
   sudo iptables -A OUTPUT -p udp --sport 50000:50002 -j ACCEPT
   ```

## Runtime Optimization

For maximum throughput:

1. Assign CPU cores to the applications:
   ```
   taskset -c 0,1 ./c_application
   taskset -c 2,3 python main2.py
   ```

2. Increase process priority:
   ```
   sudo nice -n -10 ./c_application
   sudo nice -n -10 python main2.py
   ```

3. Monitor packet statistics with:
   ```
   netstat -su
   ```

## Troubleshooting

1. If excessive packet loss persists:
   - Verify network switch/router configurations
   - Consider implementing a custom acknowledgment protocol
   - Reduce message size (currently set to 60KB per packet)
   - Adjust MESSAGE_INTERVAL in global_vars.py

2. For system resource issues:
   - Check available memory: `free -m`
   - Monitor CPU usage: `top` or `htop`
   - Verify file descriptor usage: `lsof | wc -l`