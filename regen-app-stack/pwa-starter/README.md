# RegenHub PWA Starter

A minimal, production-ready PWA starter template using **Rust + Leptos + Trunk**. Ships as a WASM web app that installs like native — no App Store, no 30% tax, no gatekeepers.

## Quick Start (5 minutes)

### Option A: Docker (No Rust needed)

```bash
# Build and run in one command
docker build -t regen-pwa-builder .
docker run --rm -p 8080:8080 -v $(pwd):/app regen-pwa-builder

# Open http://localhost:8080
```

### Option B: Local Development

```bash
# 1. Install Rust (one-time)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Add WASM target
rustup target add wasm32-unknown-unknown

# 3. Install Trunk
cargo install trunk

# 4. Serve the app
trunk serve

# Open http://localhost:8080
```

### Build for Production

```bash
# Development build (with debugging)
trunk build

# Production build (optimized)
trunk build --release
# Output in ./dist/
```

---

## What You Get

- **Rust → WASM compilation** via Leptos + Trunk
- **PWA manifest** with installability metadata
- **Service worker** for offline functionality
- **App shell caching** for instant loads
- **HTTPS-ready** deployment config
- **Docker setup** for building without local Rust

---

## Project Structure

```
pwa-starter/
├── Cargo.toml           # Rust dependencies
├── build.rs             # Trunk build hook
├── Trunk.toml           # Trunk configuration
├── Dockerfile           # Containerized build (no Rust needed)
├── index.html           # HTML entry point
├── public/
│   ├── manifest.json    # PWA manifest
│   ├── sw.js            # Service worker
│   └── icons/           # App icons
└── src/
    └── main.rs          # Rust application
```

---

## Deployment

### Static Hosting (Recommended)

The `dist/` folder (after `trunk build`) contains everything you need. Deploy to:

- **Cloudflare Pages**: Zero-config, global CDN, free
- **Netlify**: Drag-and-drop or git deploy, free tier
- **Vercel**: Similar to Netlify
- **Self-hosted**: Any web server (nginx, Caddy, Apache)
- **IPFS**: For decentralized, censorship-resistant hosting

### HTTPS Requirement

PWAs **require HTTPS** for:
- Service workers
- Push notifications
- Geolocation
- Device hardware access

Most hosts provide free HTTPS (Let's Encrypt). For self-hosted:

```bash
# Caddy (automatic HTTPS)
caddy reverse-proxy --from yourdomain.com --to localhost:8080

# nginx with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Dockerfile for Production Build

```dockerfile
# Build stage
FROM rust:1.77-slim as builder
RUN apt-get update && apt-get install -y libssl-dev pkg-config
RUN rustup target add wasm32-unknown-unknown
RUN cargo install trunk
WORKDIR /app
COPY . .
RUN trunk build --release --dist /app/dist

# Serve stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf (Production)

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Gzip compression
        gzip on;
        gzip_types text/css application/javascript application/wasm;

        # Long cache for immutable assets (WASM/JS chunks)
        location /pkg/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # SPA fallback
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
}
```

---

## Verifying Your PWA

1. **Lighthouse Audit**: In Chrome DevTools → Lighthouse → "Progressive Web App"
2. **PWA Builder**: https://www.pwabuilder.com/ — paste your URL for detailed report
3. **Webhint**: https://webhint.io/ — accessibility, performance, security

### Manual Install Test

1. Serve the app over HTTPS
2. Chrome: DevTools → Application → Service Workers
3. Look for "Install" button or address bar install icon

---

## Customization

### Change App Name/Branding

Edit `public/manifest.json`:
```json
{
    "name": "Your App Name",
    "short_name": "App",
    "theme_color": "#your-color"
}
```

### Update Icons

Replace files in `public/icons/`:
- `icon.svg` — source vector (recommended)
- `icon-192.png` — 192×192 PNG
- `icon-512.png` — 512×512 PNG
- `icon-maskable.png` — 512×512 with safe zone (for Android adaptive icons)

Generate from SVG:
```bash
# Using ImageMagick
convert -background none icon.svg -resize 192x192 icon-192.png
convert -background none icon.svg -resize 512x512 icon-512.png
```

### Add Dependencies

Edit `Cargo.toml`, then rebuild:
```toml
[dependencies]
leptos = { version = "0.7", features = ["wasm-bindgen-futures"] }
# Add your crates here
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

---

## Troubleshooting

### "Cannot find wasm32 target"

```bash
rustup target add wasm32-unknown-unknown
```

### "trunk: command not found"

```bash
cargo install trunk
```

### Service worker not registering

- Check you're serving over HTTPS (or localhost)
- Open DevTools → Application → Service Workers for errors
- Clear site data: DevTools → Application → Clear storage

### WASM not loading

- Check the browser console for fetch errors
- Ensure `public/pkg/` directory exists after build
- Verify your server has correct MIME types for `.wasm` and `.js`

---

## Philosophy

This template exists because **users should control their software**. Not Apple, not Google, not any corporation.

With a PWA:
- Users install directly from your domain
- Updates flow directly from you (no App Store review delays)
- The app works offline (no excuse for "no connection" walls)
- No 30% revenue tax
- No de-platforming risk
- Users can verify the source (it's all open!)

Build for the web. Respect your users. Ship directly.
