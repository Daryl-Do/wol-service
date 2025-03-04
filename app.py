import os
import re
import json
import socket
import struct
import sys
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load machine configurations from environment variables
def load_machines():
    """
    Load machine configurations from environment variables.
    Both formats are supported:
    - MACHINE_NAME=XX:XX:XX:XX:XX:XX (legacy)
    - NAME=XX:XX:XX:XX:XX:XX
    """
    machines = {}
    
    # Check all environment variables
    for name, value in os.environ.items():
        # Normalize both variable name and MAC to lowercase
        name = name.lower()
        value = value.strip().lower()
        
        # Check if this is a MAC address
        if re.match(r'^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$', value):
            # Remove MACHINE_ prefix if present
            if name.startswith('machine_'):
                name = name[8:]
            
            # Normalize MAC address format to use colons
            mac = value.replace('-', ':')
            machines[name] = mac
    
    return machines

# Load machines at startup
MACHINES = load_machines()

def send_magic_packet(mac_address, broadcast_ip='255.255.255.255'):
    """
    Sends a magic packet to wake up a machine with the given MAC address.
    
    Args:
        mac_address: The MAC address of the target machine
        broadcast_ip: The broadcast IP to send the packet to (default: 255.255.255.255)
    """
    logger.info(f"===== Sending WoL packet to {mac_address} =====")
    # Convert MAC address to bytes
    mac_bytes = bytearray.fromhex(mac_address.replace(':', ''))
    
    # Create magic packet: 6 bytes of 0xFF followed by 16 repetitions of the MAC address
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    
    # Send packet to the broadcast address
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Try sending to multiple common broadcast addresses
        broadcast_addresses = [broadcast_ip]
        
        # Add user-provided broadcast address from environment if available
        user_broadcast = os.environ.get('BROADCAST_IP')
        if user_broadcast and user_broadcast != broadcast_ip:
            broadcast_addresses.append(user_broadcast)
            logger.info(f"Using environment BROADCAST_IP: {user_broadcast}")
            
        # Add common subnet broadcast addresses
        for subnet in ['192.168.0.255', '192.168.1.255', '10.0.0.255', '10.0.1.255', '192.168.31.255']:
            if subnet != broadcast_ip and subnet != user_broadcast:
                broadcast_addresses.append(subnet)
        
        logger.info(f"Will attempt sending to these broadcast addresses: {broadcast_addresses}")
        
        # Send to all broadcast addresses
        for addr in broadcast_addresses:
            try:
                sock.sendto(magic_packet, (addr, 9))  # Port 9 is common for WoL
                logger.info(f"Magic packet sent to {addr}")
            except Exception as e:
                logger.error(f"Failed to send to {addr}: {e}")
    
    return True

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "Wake-on-LAN service is running",
        "machines": list(MACHINES.keys())
    })

@app.route('/<machine_name>')
def wake_machine(machine_name):
    machine_name = machine_name.lower()
    
    # Extract optional broadcast IP from the query string
    broadcast_ip = request.args.get('broadcast', '255.255.255.255')
    
    if machine_name not in MACHINES:
        return jsonify({
            "status": "error",
            "message": f"Unknown machine: {machine_name}",
            "available_machines": list(MACHINES.keys())
        }), 404
    
    mac_address = MACHINES[machine_name]
    result = send_magic_packet(mac_address, broadcast_ip)
    
    if result:
        return jsonify({
            "status": "success",
            "message": f"Magic packet sent to {machine_name} ({mac_address})"
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Failed to send magic packet to {machine_name} ({mac_address})"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 12580))
    
    if not MACHINES:
        logger.warning("No machines configured. Set environment variables like MACHINE_NAME=XX:XX:XX:XX:XX:XX")
    else:
        logger.info(f"Configured machines: {list(MACHINES.keys())}")
    
    # Enable debug mode for more verbose output
    app.run(host='0.0.0.0', port=port, debug=True) 