# Wake-on-LAN (WoL) Docker Service

A very lightweight Docker application to wake up local machines using Wake-on-LAN (WoL)

一个非常轻量的wol服务，实现内网远程开机。

You can integete with IOS shortcut or NFC tag.

可以配合使用IOS的shortcut，或者NFC的贴纸。

## Features

- Minimal memory usage : about 38 Mb
- Simple HTTP API to wake up machines by name, configured by docker-compose or docker-run
- Supports multiple machines

## Prerequisites

1. Docker installed on your host system
2. Wake-on-LAN enabled on the target machines
3. The MAC and IP addresses of the target machines acquired
4. Target machines must be on the same network as the Docker host

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


## License

This project is open source and available under the MIT License. 