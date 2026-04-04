# n8n Installation & Management

## Overview
n8n is a workflow automation tool deployed via Docker on port 5678.

## Quick Start
```bash
cd ~/infra/n8n
./deploy_n8n.sh
```

## Manual Commands
```bash
# Start
docker compose -f docker-compose.n8n.yml up -d

# Stop
docker compose -f docker-compose.n8n.yml down

# View logs
docker logs -f n8n

# Restart
docker compose -f docker-compose.n8n.yml restart
```

## Access
- Local: `http://localhost:5678`
- LAN: `http://<server-ip>:5678` (allowed from 192.168.4.0/22)
- On first visit, you'll be prompted to create an owner account.

## Firewall
UFW rule added (server LAN is /22, not /24):
```
sudo ufw allow from 192.168.4.0/22 to any port 5678 proto tcp comment "n8n workflow automation"
```

## Configuration
- Data is persisted in `./data/` (mapped to `/home/node/.n8n` in the container)
- Timezone defaults to `America/New_York` (edit `docker-compose.n8n.yml` to change)

## Upgrading
```bash
docker compose -f docker-compose.n8n.yml pull
./deploy_n8n.sh
```

## File Structure
```
~/infra/n8n/
├── docker-compose.n8n.yml    # Container definition
├── deploy_n8n.sh             # Deploy/start script
├── README.md                 # This file
└── data/                     # Persistent n8n data
```
