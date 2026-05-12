#!/bin/bash
set -e

DOMAIN="thearticleanalyzer.com"
APP_DIR="/root/AiArticleAnalyzer"
REPO="https://github.com/mohammedAlbalushi582/AiArticleAnalyzer.git"

echo "========================================="
echo " Deploying $DOMAIN"
echo "========================================="

# --- 1. System updates & dependencies ---
echo "[1/8] Updating system and installing dependencies..."
apt-get update -y
apt-get install -y curl git nginx certbot python3-certbot-nginx ufw

# --- 2. Install Docker ---
if ! command -v docker &> /dev/null; then
    echo "[2/8] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "[2/8] Docker already installed, skipping..."
fi

# --- 3. Firewall ---
echo "[3/8] Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# --- 4. Clone repo ---
echo "[4/8] Cloning repository..."
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO" "$APP_DIR"
    cd "$APP_DIR"
fi

# --- 5. Create env files ---
echo "[5/8] Setting up environment files..."

# Generate a random Django secret key
DJANGO_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
PG_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

if [ ! -f backend/.env ]; then
    read -rp "Enter your Anthropic API key: " ANTHROPIC_KEY
    cat > backend/.env <<EOF
DJANGO_SECRET_KEY=$DJANGO_SECRET
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,127.0.0.1
DATABASE_URL=postgres://postgres:$PG_PASSWORD@db:5432/article_analyzer
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
DJANGO_SETTINGS_MODULE=config.settings.prod
EOF
    echo "  -> backend/.env created"
else
    echo "  -> backend/.env already exists, skipping..."
fi

# Export PG password for docker-compose
export POSTGRES_PASSWORD=$PG_PASSWORD

# --- 6. Build & start containers ---
echo "[6/8] Building and starting Docker containers..."
docker compose -f docker-compose.prod.yml up --build -d

# Wait for backend to be ready
echo "  -> Waiting for backend to be ready..."
sleep 10

# --- 7. Nginx config ---
echo "[7/8] Configuring Nginx..."

# Start with HTTP-only config for certbot
cat > /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
mkdir -p /var/www/certbot
nginx -t && systemctl restart nginx

# --- 8. SSL Certificate ---
echo "[8/8] Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --redirect --email admin@$DOMAIN || {
    echo ""
    echo "WARNING: SSL certificate failed. This usually means DNS is not pointing to this server yet."
    echo "Once DNS is configured, run:"
    echo "  certbot --nginx -d $DOMAIN -d www.$DOMAIN"
    echo ""
    echo "The site is still accessible via HTTP at http://$DOMAIN"
}

echo ""
echo "========================================="
echo " Deployment complete!"
echo "========================================="
echo " Site: https://$DOMAIN"
echo " API:  https://$DOMAIN/api/"
echo ""
echo " Useful commands:"
echo "   cd $APP_DIR"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo "   docker compose -f docker-compose.prod.yml restart"
echo "========================================="
