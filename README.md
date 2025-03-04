# Wake-on-LAN (WoL) Docker Service

A very lightweight Docker application to wake up local machines using Wake-on-LAN (WoL)

## Features

- Minimal memory usage : about 38 Mb
- Simple HTTP API to wake up machines by name, configured by docker-compose or docker-run
- Supports multiple machines

## Prerequisites

- Docker installed on your host system
- Wake-on-LAN enabled on the target machines
- The MAC and IP addresses of the target machines
- Target machines must be on the same network as the Docker host

## Quick Start

### Using Docker Run

```bash
docker run -d \
  --name wol-service \
  -p 12580:12580 \
  -e PC1=00:11:22:33:44:55 \
  -e PC2=AA:BB:CC:DD:EE:FF \
  -e BROADCAST_IP=192.168.1.255 \
  --restart unless-stopped \
  $(docker build -q .)
```

Replace `00:11:22:33:44:55` and `AA:BB:CC:DD:EE:FF` with the actual MAC addresses of your machines. Set `BROADCAST_IP` to your specific network's broadcast address (typically your subnet with the last octet set to 255, e.g., 192.168.1.255).

### Using Docker Compose

1. Clone this repository or create the files as shown in the repository.
2. Edit the `docker-compose.yml` file to add your machine information:

```yaml
environment:
  - pc1=00:11:22:33:44:55  # Replace with your actual MAC address
  - pc2=AA:BB:CC:DD:EE:FF  # Replace with your actual MAC address
  - BROADCAST_IP=192.168.1.255  # Replace with your network's broadcast address
```

3. Start the service:

```bash
docker compose up -d
```

## Usage

Once the container is running, you can wake up a machine by accessing:

```
http://localhost:12580/machine_name
```

Where `machine_name` is the name you provided in the environment variables (without the `MACHINE_` prefix).

For example:
- `http://localhost:12580/pc1` will wake up the machine with MAC address configured as `PC1`
- `http://localhost:12580/pc2` will wake up the machine with MAC address configured as `PC2`

You can also specify a custom broadcast address for a specific request:

```
http://localhost:12580/machine_name?broadcast=192.168.1.255
```

This is particularly useful when using Docker on macOS or Windows where the Docker network is isolated from your host network.

You can also access `http://localhost:12580/` to get a list of available machines.

## Environment Variables

- `PORT`: The port on which the service will listen (default: 12580)
- `BROADCAST_IP`: The broadcast IP address to send magic packets to (helpful for Docker on macOS/Windows)
- You can define machines using any environment variable with a MAC address as its value:
  - Direct naming: `mypc=XX:XX:XX:XX:XX:XX` 
  - With prefix (for backwards compatibility): `MACHINE_mypc=XX:XX:XX:XX:XX:XX`
  - All names are case-insensitive

## Building the Image

If you want to build the Docker image yourself:

```bash
docker build -t wol-service .
```

## Troubleshooting

1. Make sure Wake-on-LAN is enabled in the BIOS/UEFI of the target machines.
2. Ensure the target machines are configured to respond to WoL magic packets.
3. The Docker host and target machines must be on the same network.
4. Some networks might block broadcast packets, which are required for WoL to work.

### Docker on macOS/Windows

If you're running Docker on macOS or Windows, you'll need to set the `BROADCAST_IP` environment variable to your network's broadcast address (e.g., 192.168.1.255), as Docker runs in a virtual machine and cannot directly access the host's network.

To find your broadcast address:
- On macOS: Run `ifconfig` in Terminal and look for your active interface (en0 for WiFi, en1 for Ethernet typically)
- On Windows: Run `ipconfig` in Command Prompt and look for your active adapter

Once you know your IP address (e.g., 192.168.1.100) and subnet mask (e.g., 255.255.255.0), your broadcast address will typically be your subnet with the last octet set to 255 (e.g., 192.168.1.255).

## License

This project is open source and available under the MIT License. 