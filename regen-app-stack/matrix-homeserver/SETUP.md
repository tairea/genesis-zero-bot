# Matrix Homeserver Setup

**Self-host a Matrix homeserver for community communication — no corporate surveillance, no de-platforming.**

Matrix is an open protocol for real-time communication. Unlike Discord, Slack, or WhatsApp:
- You own your server (and your data)
- Messages are end-to-end encrypted by default in private rooms
- Federation means your server can communicate with other Matrix servers
- No single corporation controls the network

This guide sets up **Synapse** (the reference Matrix homeserver) with **Docker Compose**.

---

## Quick Start (15 minutes)

```bash
cd matrix-homeserver

# 1. Edit docker-compose.yml — set your domain and passwords
vim docker-compose.yml

# 2. Generate the Matrix configuration
docker compose run --rm generate

# 3. Start the server
docker compose up -d

# 4. Register your admin user
docker compose run --rm register admin-password-here

# 5. Access Element Web at http://localhost:8080
```

---

## Prerequisites

- **Domain name** (or subdomain) pointed to your server
- **Docker** and **Docker Compose** installed
- **Port 80 and 443** open on your firewall
- **Linux server** (this guide assumes Debian/Ubuntu)

### Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Verify
docker --version
```

### Install Docker Compose

```bash
# Download docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker compose version
```

---

## Configuration

### 1. Create the docker-compose.yml

```yaml
version: '3.8'

services:
  # The Matrix homeserver (Synapse)
  synapse:
    image: matrixdotorg/synapse:latest
    container_name: matrix-synapse
    restart: unless-stopped
    ports:
      - "8008:8008"  # Unencrypted HTTP (for reverse proxy)
      - "8448:8448"  # Federation port
    volumes:
      - ./data:/data
      - ./synapse:/synapse
    environment:
      - SYNAPSE_SERVER_NAME=your-domain.com
      - SYNAPSE_REPORT_STATS=no
    env_file:
      - synapse.env

  # Element Web - The Matrix client UI
  element:
    image: vectorized/element-web:latest
    container_name: matrix-element
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./element-config:/usr/share/nginx/html/config
    depends_on:
      - synapse

  # PostgreSQL database (required for production)
  postgres:
    image: postgres:15-alpine
    container_name: matrix-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=synapse
      - POSTGRES_USER=synapse
      - POSTGRES_PASSWORD=CHANGE_ME_IN_ENV_FILE
    volumes:
      - ./postgres:/var/lib/postgresql/data

networks:
  default:
    name: matrix-network
```

### 2. Create synapse.env

```bash
# Domain name (no https://)
SYNAPSE_SERVER_NAME=matrix.your-domain.com

# Database configuration
SYNAPSE_DB_HOST=postgres
SYNAPSE_DB_PORT=5432
SYNAPSE_DB_NAME=synapse
SYNAPSE_DB_USER=synapse
SYNAPSE_DB_PASS=CHANGE_ME_super_secret_password

# Registration settings
SYNAPSE_ENABLE_REGISTRATION=true
SYNAPSE_ALLOW_GUEST_ACCESS=false

# Security
SYNAPSE_ACME_STORAGE=/data/acme
SYNAPSE_HTTP_RESOURCES=[{paths=["/.well-known/matrix"], resources=["client"]}]

# Reporting
SYNAPSE_REPORT_STATS=no
```

### 3. Generate Synapse Config

```bash
# Generate initial config
docker compose run --rm -e SYNAPSE_SERVER_NAME=matrix.your-domain.com \
  matrixdotorg/synapse generate

# This creates:
#   homeserver.yaml in ./synapse/
#   .well-known/ directory
```

### 4. Configure Registration

Edit `synapse/homeserver.yaml`:

```yaml
# Enable registration (set to false for invite-only)
enable_registration: true

# Require email verification
enable_set_identity_server: false
registration_requires_token: false

# Session lifetime
session_refresh_token_lifetime: 86400
non_refreshable_token_lifetime: 864000

# CAPTCHA (optional, use hcaptcha or recaptcha)
# recaptcha_public_key: "YOUR_PUBLIC_KEY"
# recaptcha_private_key: "YOUR_PRIVATE_KEY"
# enable_registration_captcha: true
```

---

## Domain Setup

### DNS Records

Create these DNS records for `matrix.your-domain.com`:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | matrix | YOUR_SERVER_IP | 300 |
| AAAA | matrix | YOUR_IPV6 | 300 |

### .well-known/matrix

This tells other Matrix servers and clients how to reach your server:

```bash
# Create the directory
mkdir -p .well-known/matrix

# Create the client file
cat > .well-known/matrix/client << 'EOF'
{
    "m.server": "matrix.your-domain.com:443"
}
EOF

# Create the server file
cat > .well-known/matrix/server << 'EOF'
{
    "m.server": "matrix.your-domain.com:443"
}
EOF

# Or serve via nginx at /.well-known/matrix/
```

### Serving .well-known via Nginx

Add to your nginx config:

```nginx
location /.well-known/matrix {
    return 200 '{"m.server": "matrix.your-domain.com:443"}';
    default_type application/json;
    add_header Access-Control-Allow-Origin *;
}
```

Or via Caddy:

```caddy
matrix.your-domain.com {
    reverse_proxy localhost:8008
}

.your-domain.com/.well-known/matrix {
    respond `{"m.server": "matrix.your-domain.com:443"}` 200 {
        content_type application/json
        header Access-Control-Allow-Origin "*"
    }
}
```

---

## Reverse Proxy (HTTPS)

### Option A: Caddy (Recommended)

Caddy automatically handles HTTPS via Let's Encrypt:

```caddy
# Caddyfile
matrix.your-domain.com {
    reverse_proxy localhost:8008
}

element.your-domain.com {
    root * /var/www/element
    file_server
}
```

### Option B: Nginx

```nginx
# /etc/nginx/sites-available/matrix
server {
    listen 80;
    server_name matrix.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name matrix.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/matrix.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/matrix.your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8008;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        
        # Required for WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Get SSL certificate
sudo certbot --nginx -d matrix.your-domain.com
```

---

## User Registration

### Create Admin User

```bash
# Register a regular user
docker compose exec synapse register_new_matrix_user \
    http://localhost:8008

# Or create admin user directly
docker compose run --rm register_admin \
    --user admin \
    --password YOUR_ADMIN_PASSWORD \
    --admin \
    http://localhost:8008
```

The registration utility will ask for a shared secret (found in `synapse/homeserver.yaml`).

### Enable Open Registration

For open registration (anyone can create an account):

```bash
echo "SYNAPSE_ENABLE_REGISTRATION=true" >> synapse.env
docker compose restart synapse
```

For **invite-only** (recommended for private communities):

```bash
echo "SYNAPSE_ENABLE_REGISTRATION=false" >> synapse.env
```

Then admins can create invites:
1. Log into Element Web as admin
2. Create a private room
3. Invite users via their Matrix ID (`@user:domain.com`)

---

## JWT Authentication (Optional)

Replace the default Matrix auth with JWT tokens for SSO integration:

```yaml
# In homeserver.yaml
jwt_modules:
  - module: jwt_auth.JwtAuthenticator
    config:
      algorithm: HS256
      secret: "your-secret-key-change-in-production"
      iss: "your-domain.com"
```

---

## Element Web Deployment

Element is the most popular Matrix client. We deployed it in docker-compose.yml.

### Configure Element

Create `element-config/config.json`:

```json
{
    "defaultServerName": "matrix.your-domain.com",
    "brand": "RegenTribes",
    "elementUrl": "https://element.your-domain.com",
    "defaultCountryCode": "US",
    "showLabsFlags": false,
    "features": {
        "feature_new_room_drawer": true,
        "feature_voice_broadcast": true
    }
}
```

### Update to Latest Version

```bash
docker compose pull element
docker compose up -d element
```

---

## Daily Backups

### Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
# Matrix Homeserver Backup Script

BACKUP_DIR="./backups"
DATE=$(date +%Y-%m-%d_%H-%M)
mkdir -p $BACKUP_DIR

# Stop the server to ensure consistent backup
docker compose stop synapse postgres

# Backup PostgreSQL
docker compose exec -T postgres pg_dump -U synapse synapse > $BACKUP_DIR/synapse_db_$DATE.sql

# Backup Synapse data
tar -czf $BACKUP_DIR/synapse_data_$DATE.tar.gz ./data ./synapse

# Backup Element config
tar -czf $BACKUP_DIR/element_config_$DATE.tar.gz ./element-config

# Restart services
docker compose start synapse postgres

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

echo "Backup complete: $DATE"
```

```bash
chmod +x backup.sh
```

### Schedule Daily Backups

```bash
# Add to crontab
crontab -e

# Run daily at 3 AM
0 3 * * * /path/to/matrix-homeserver/backup.sh >> /path/to/backups/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop services
docker compose stop synapse postgres

# Restore database
cat backups/synapse_db_2024-01-15.sql | docker compose exec -T postgres psql -U synapse synapse

# Restore data
tar -xzf backups/synapse_data_2024-01-15.tar.gz

# Restart
docker compose start synapse postgres
```

---

## Security Checklist

### Firewall

```bash
# UFW example
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8448/tcp  # Federation (optional, for outgoing connections)
sudo ufw enable
```

### Matrix-Specific Hardening

In `homeserver.yaml`:

```yaml
# Disable public rooms discovery
allow_public_rooms_over_federation: false

# Restrict who can create rooms
restrict_room_creation: true

# Require authentication for all endpoints
require_auth_for_profile_options: true

# Rate limiting
rc_messages_per_second: 0.2
rc_registration_rate_limit:
  per_registration_seconds: 60
  count: 3
```

### 2FA / E2E Encryption

Matrix uses end-to-end encryption by default for DMs and private rooms. As an admin:

1. Log into Element as admin
2. Go to Settings → Security → Encryption
3. Enable "Manage encryption keys" to set up recovery

For maximum security, disable non-E2E rooms:

```yaml
# In homeserver.yaml — disable non-encrypted rooms
encryption_enabled_by_default_for_room_type: invite
```

### Regular Updates

```bash
# Update Synapse
docker compose pull synapse
docker compose up -d synapse

# Update Postgres
docker compose pull postgres
docker compose up -d postgres

# Update Element
docker compose pull element
docker compose up -d element
```

---

## Telegram Bridge

Connect Matrix rooms to Telegram groups for bridging with non-Matrix users.

### Setup mx-puppet-telegram

Add to `docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  mx-puppet-telegram:
    image: sorunome/mx-puppet-telegram:latest
    container_name: matrix-telegram
    restart: unless-stopped
    ports:
      - "8430:8430"
    volumes:
      - ./telegram:/data
    environment:
      - SYNAPSE_URL=http://synapse:8008
      - SYNAPSE_SECRET=YOUR_SYNAPSESharedSecret
      - TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    depends_on:
      - synapse
```

### Configure Bridge

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Get the bot token
3. Start the bridge:
   ```bash
   docker compose up -d mx-puppet-telegram
   ```
4. In Element, message `@telegrambot:your-domain.com`
5. Follow prompts to link your Telegram account

### Bridge Configuration

Edit `helegram-config.yaml`:

```yaml
# Bridge settings
bridge:
  domain: matrix.your-domain.com
  
  # Port for puppeting
  port: 8430
  bindAddress: 0.0.0.0
  
  # Database
  database: postgresql://synapse:synapse_password@postgres:5432/telegram_puppet
  
  # Logging
  logLevel: info
```

---

## Monitoring

### Health Check

```bash
# Check server status
curl http://localhost:8008/_matrix/client/versions

# Should return:
# {"versions":["r0.0.0","r0.1.0","r0.2.0","r0.3.0","r0.4.0","r0.5.0","r0.6.0","v1.1","v1.2","v1.3","v1.4","v1.5","v1.6","v1.7","v1.8","v1.9"]}
```

### View Logs

```bash
# Synapse logs
docker compose logs -f synapse

# All services
docker compose logs -f
```

### Metrics (Optional)

Enable Prometheus metrics:

```yaml
# In homeserver.yaml
metrics_statistics_enabled: true
report_stats: true
```

Then add Grafana dashboard for visualization.

---

## Troubleshooting

### "Connection refused" or federation issues

1. Check firewall: `sudo ufw status`
2. Verify DNS: `dig matrix.your-domain.com`
3. Test ports: `nc -zv matrix.your-domain.com 443`

### Registration not working

1. Check `enable_registration: true` in homeserver.yaml
2. Verify the registration shared secret
3. Check logs: `docker compose logs synapse`

### Cannot receive federation messages

1. Ensure port 8448 is open (or 443 if using SRV records)
2. Verify .well-known/matrix/server is accessible
3. Test at https://federationtester.matrix.org/

### Database connection issues

```bash
# Check postgres is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Verify connection
docker compose exec synapse env | grep SYNAPSE_DB
```

---

## Related

- [Matrix Protocol](https://matrix.org/) — Official Matrix site
- [Synapse Documentation](https://matrix-org.github.io/synapse/latest/) — Admin docs
- [Element Web](https://element.io/) — Matrix client
- [Obtainium](./obtainium-config-generator.html) — APK updates via Matrix
- [PGP Key Setup](./pgp-key-setup/) — Sign your releases for trust
