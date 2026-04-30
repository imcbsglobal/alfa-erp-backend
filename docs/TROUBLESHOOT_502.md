# 502 Error Troubleshooting

## Quick Fix

```bash
ssh root@88.222.212.14

# Check service status
sudo systemctl status gunicorn-alfa-prod

# View recent errors
sudo journalctl -u gunicorn-alfa-prod -n 50 --no-pager

# Restart service
sudo systemctl restart gunicorn-alfa-prod
sudo systemctl restart nginx
```

## Common Causes

1. **Gunicorn crashed** - Restart service
2. **Port mismatch** - Check Nginx upstream matches Gunicorn port
3. **Missing dependencies** - Run `pip install -r requirements.txt`
4. **Database connection failed** - Check DB credentials in .env
5. **Permission issues** - Run `sudo chown -R www-data:www-data /var/www/alfa-erp-backend-prod/`
