EN | [RU](docs/README_RU.md)

## Solstice Meridian Site 🏥

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/Static-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![nginx](https://img.shields.io/badge/nginx-ready-009639?style=flat-square&logo=nginx&logoColor=white)

Static integrative oncology clinic website with a Python generator, SEO, clean URLs, contact API, and one-command deploy.

Built for **Solstice Meridian Oncology Institute** - 13 pages, unique images per page, responsive header, sanitized contact form.

---

## ✨ Features

- **Static generator** 🐍 - OOP Python in `clinic/`, seed-based placeholder copy
- **SEO pack** 🔍 - meta, Open Graph, Twitter cards, JSON-LD, sitemap, robots
- **Clean URLs** 🔗 - `/about`, `/categories/slug` (nginx rewrite rules included)
- **Contact API** 📬 - POST `/api/contact`, honeypot, rate limit, origin check
- **Asset pipeline** 🖼️ - harvest, dedupe, normalize images, cache-bust query params
- **Delivery pack** 📦 - `./start.sh package` builds client zip + full-page screenshots

---

## 🚀 Quick start

```bash
chmod +x start.sh
./start.sh          # build + preview http://127.0.0.1:8080
./start.sh build    # output to public/ only
```

**Windows**

```bat
start.bat
start.bat build
```

Preview serves `public/` with Python `http.server`. For clean URLs in production, use the included nginx config.

---

## 📋 Commands

| Command | Action |
|---------|--------|
| `./start.sh` / `preview` | build + local preview |
| `./start.sh build` | regenerate `public/` |
| `./start.sh deploy` | rsync to server + nginx reload + contact API |
| `./start.sh setup` | first-time nginx on remote host |
| `./start.sh package` | client delivery zip + Playwright screenshots |

---

## ⚙️ Configuration

Copy examples and fill in your values:

```bash
cp deploy/config.env.example deploy/config.env
cp deploy/contact-api.env.example deploy/contact-api.env
```

`deploy/config.env`:

```env
DOMAIN=clinic.example.com
BASE_URL=https://clinic.example.com
SSH_HOST=root@YOUR_SERVER
REMOTE_DIR=/var/www/clinic
PREVIEW_PORT=8080
```

Edit `deploy/nginx.conf` for your domain and TLS certificate paths before deploy.

---

## Structure

```
clinic/          site generator (domain, pages, SEO, assets)
static/          CSS, JS, favicon source
public/          built static site (gitignored, generated)
services/        contact form API (Python stdlib)
deploy/          nginx, systemd, env templates
_tools/          build and deploy helpers
build.py         entry point
start.sh         main CLI
```

---

## Pages

- Home
- Treatment Categories + 6 category pages
- About Us
- Our Testimonials
- Contact Us

Copy lives in `clinic/content.py`. Rebuild with another seed via `build.py`.

---

## 📸 Screenshots

Run `./start.sh package` - PNG previews land in `delivery-staging/screenshots/` and inside the client zip.

---

Thank you for reading! 🐾

**xvDosha** · [github.com/xvDoshik](https://github.com/xvDoshik) · [dosha.pw](https://dosha.pw)
