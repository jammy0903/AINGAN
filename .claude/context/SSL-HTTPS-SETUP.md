# SSL/HTTPS Setup Guide for aingan.click

## Current Status
✅ **Completed:**
- Domain registration: aingan.click (Namecheap)
- DNS A records configured: @ and www pointing to 129.154.50.35
- Nginx configuration updated for HTTPS (commit: c7d2962)
- Docker Compose HTTPS port exposed (commit: c7d2962)
- Certbot installed on Oracle Cloud VM
- Frontend NEXT_PUBLIC_API_URL set to https://aingan.click/api

⏳ **Pending:**
- DNS propagation (24-48 hours from Namecheap)
- Let's Encrypt SSL certificate generation

---

## Step-by-Step Setup (Once DNS Propagates)

### 1. Verify DNS Propagation
SSH into Oracle Cloud VM and test DNS resolution:
```bash
ssh -i ~/.ssh/oracle_aingan ubuntu@129.154.50.35
curl -I http://aingan.click  # Should get 200 response
```

### 2. Generate SSL Certificate with Certbot
Once DNS is confirmed, run this command on the VM:
```bash
sudo certbot certonly --standalone \
  -d aingan.click \
  -d www.aingan.click \
  --agree-tos \
  --non-interactive \
  -m fuso3367@kakao.com
```

**Why `--standalone`?**
- We're using Nginx as reverse proxy in Docker
- Certbot will temporarily start its own server to validate domain ownership
- This is simpler than `--webroot` for Docker setups

### 3. Verify Certificate Generation
Certificates should be created at:
- `/etc/letsencrypt/live/aingan.click/fullchain.pem`
- `/etc/letsencrypt/live/aingan.click/privkey.pem`

Check with:
```bash
sudo ls -la /etc/letsencrypt/live/aingan.click/
```

### 4. Restart Nginx Container
After certificate generation, restart the stack:
```bash
cd /home/ubuntu/AINGAN
docker compose restart nginx
```

### 5. Test HTTPS Access
```bash
curl -I https://aingan.click/
curl -I https://www.aingan.click/

# Test API endpoint
curl -I https://aingan.click/api/posts
```

### 6. Configure Automatic Renewal
Let's Encrypt certificates expire after 90 days. Add auto-renewal:

```bash
# Test renewal process
sudo certbot renew --dry-run

# Create a cron job for automatic renewal (runs twice daily)
sudo crontab -e

# Add this line:
0 */12 * * * certbot renew --quiet
```

---

## Nginx Configuration Details

### HTTP → HTTPS Redirect
```nginx
server {
    listen 80;
    server_name aingan.click www.aingan.click;
    return 301 https://$server_name$request_uri;
}
```

### HTTPS Server Block
```nginx
server {
    listen 443 ssl http2;
    server_name aingan.click www.aingan.click;

    # SSL certificates (Let's Encrypt via Certbot)
    ssl_certificate     /etc/letsencrypt/live/aingan.click/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aingan.click/privkey.pem;

    # SSL security configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
}
```

---

## Docker Compose Configuration

The following updates were made to expose HTTPS port and mount certificates:

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"  # ← Added for HTTPS
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    - /etc/letsencrypt:/etc/letsencrypt:ro  # ← Added for SSL certs
  depends_on:
    - backend
    - frontend
```

---

## Environment Variables

Frontend API endpoint is already configured:
```yaml
environment:
  - NEXT_PUBLIC_API_URL=https://aingan.click/api
```

This means:
- Browser requests from external clients go to `https://aingan.click/api`
- Docker internal communication still uses `http://backend:8000`

---

## Troubleshooting

### Certificate Not Found Error
```
[error] 123#123: *1 "/etc/nginx/ssl/cert.pem" failed (2: No such file or directory)
```
**Solution:** Certbot hasn't been run yet, or certificates weren't generated successfully.

Check:
```bash
sudo ls /etc/letsencrypt/live/aingan.click/
# If empty, DNS hasn't propagated or Certbot failed
```

### DNS Not Resolving
```bash
# Check with:
sudo systemctl restart systemd-resolved
# Flush DNS cache
sudo systemctl restart networking
```

### Certbot Permission Issues
If you get permission denied errors:
```bash
sudo chown -R root:root /etc/letsencrypt
sudo chmod -R 755 /etc/letsencrypt
```

### Port 443 Already in Use
```bash
sudo lsof -i :443
# Kill any process using port 443 before starting containers
```

---

## Security Best Practices

✅ **Implemented:**
- HTTP/2 support (faster, multiplexed connections)
- Strong SSL/TLS protocols (TLS 1.2 & 1.3)
- Strong cipher suites (no weak algorithms)
- SSL session caching (performance optimization)
- HTTP → HTTPS redirect (always encrypted)

🔒 **Additional Options (Future):**
- HSTS headers (HTTP Strict Transport Security)
- Certificate pinning
- Regular security audits with `ssl-labs.com`

---

## Testing After SSL Activation

```bash
# Check SSL configuration
openssl s_client -connect aingan.click:443

# Test with curl
curl -vvv https://aingan.click/

# Grade your SSL at
# https://www.ssllabs.com/ssltest/?d=aingan.click
```

---

## Timeline
- ✅ Feb 14, 2026: Domain setup + Nginx/Docker config
- ⏳ Feb 14-16, 2026: DNS propagation (24-48 hours)
- ⏳ After propagation: Certbot certificate generation
- ⏳ After certs: Manual test + restart containers
- ✅ Ongoing: Automatic renewal via cron

---

## Next Actions
1. **Monitor DNS propagation** at [mxtoolbox.com](https://mxtoolbox.com/MXLookup.aspx)
2. **Once DNS resolves**, run the Certbot command in Step 2 above
3. **Restart Nginx** container
4. **Test HTTPS access** at https://aingan.click
5. **Update Vercel** frontend if needed (already configured via docker-compose)
