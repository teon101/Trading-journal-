# TradeJournal Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Python 3.8+
- SQLite 3
- Nginx (recommended)
- SSL Certificate

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y

# Create app directory
sudo mkdir -p /var/www/tradejournal
cd /var/www/tradejournal
```

### 2. Application Setup
```bash
# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Install Playwright browsers
playwright install chromium
```

### 3. Environment Configuration
```bash
# Create production .env file
cp .env.example .env
nano .env
```

Set production values:
```env
SECRET_KEY=<generate-secure-random-key>
FLASK_ENV=production
DATABASE_PATH=/var/www/tradejournal/database/trading_journal.db
```

Generate secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create initial admin user
python manage.py create-user

# Create backup schedule
python manage.py backup
```

### 5. Gunicorn Setup

Create `/etc/systemd/system/tradejournal.service`:
```ini
[Unit]
Description=TradeJournal WSGI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tradejournal
Environment="PATH=/var/www/tradejournal/venv/bin"
ExecStart=/var/www/tradejournal/venv/bin/gunicorn --workers 3 --bind unix:tradejournal.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start tradejournal
sudo systemctl enable tradejournal
```

### 6. Nginx Configuration

Create `/etc/nginx/sites-available/tradejournal`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/tradejournal/tradejournal.sock;
    }

    location /static {
        alias /var/www/tradejournal/app/static;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/tradejournal /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 8. Automated Backups

Add to crontab:
```bash
crontab -e
```

Add daily backup:
```
0 2 * * * cd /var/www/tradejournal && /var/www/tradejournal/venv/bin/python manage.py backup
```

### 9. Monitoring

Check application logs:
```bash
sudo journalctl -u tradejournal -f
```

Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

### 10. Updates
```bash
cd /var/www/tradejournal
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
sudo systemctl restart tradejournal
```

## 🔒 Security Checklist

- [ ] Change SECRET_KEY
- [ ] Set FLASK_ENV=production
- [ ] Enable firewall (UFW)
- [ ] Set up SSL certificate
- [ ] Configure database backups
- [ ] Set file permissions correctly
- [ ] Disable debug mode
- [ ] Use strong passwords
- [ ] Enable rate limiting
- [ ] Set up monitoring

## 📊 Performance Tips

1. Use Redis for caching
2. Enable gzip compression
3. Optimize database queries
4. Use CDN for static files
5. Monitor resource usage