[EN](../README.md) | RU

## Solstice Meridian Site 🏥

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/Static-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![nginx](https://img.shields.io/badge/nginx-ready-009639?style=flat-square&logo=nginx&logoColor=white)

Статический сайт интегративной онкологической клиники: Python-генератор, SEO, чистые URL, API формы обратной связи, деплой одной командой.

Проект **Solstice Meridian Oncology Institute** - 13 страниц, уникальные картинки на страницу, адаптивный header, санитизация контактной формы.

---

## ✨ Features

- **Генератор** 🐍 - OOP Python в `clinic/`, placeholder-тексты с seed
- **SEO** 🔍 - meta, Open Graph, Twitter, JSON-LD, sitemap, robots
- **Чистые URL** 🔗 - `/about`, `/categories/slug` (nginx в комплекте)
- **Contact API** 📬 - POST `/api/contact`, honeypot, rate limit, проверка Origin
- **Ассеты** 🖼️ - сбор, дедуп, нормализация JPEG, cache-bust `?v=`
- **Пакет заказчику** 📦 - `./start.sh package` - zip + скриншоты всех страниц

---

## 🚀 Quick start

```bash
chmod +x start.sh
./start.sh          # сборка + превью http://127.0.0.1:8080
./start.sh build    # только public/
```

**Windows**

```bat
start.bat
start.bat build
```

---

## 📋 Commands

| Команда | Действие |
|---------|----------|
| `./start.sh` / `preview` | сборка + локальный сервер |
| `./start.sh build` | пересборка `public/` |
| `./start.sh deploy` | rsync на сервер + nginx + contact API |
| `./start.sh setup` | первичная настройка nginx |
| `./start.sh package` | zip для заказчика + скриншоты Playwright |

---

## ⚙️ Configuration

```bash
cp deploy/config.env.example deploy/config.env
cp deploy/contact-api.env.example deploy/contact-api.env
```

Пример `deploy/config.env`:

```env
DOMAIN=clinic.example.com
BASE_URL=https://clinic.example.com
SSH_HOST=root@YOUR_SERVER
REMOTE_DIR=/var/www/clinic
PREVIEW_PORT=8080
```

Перед деплоем поправь `deploy/nginx.conf` под свой домен и пути к TLS-сертификатам.

---

## Structure

```
clinic/          генератор
static/          CSS, JS, favicon
public/          готовый сайт (в git не попадает)
services/        API контактной формы
deploy/          nginx, systemd, env-шаблоны
_tools/          скрипты сборки и деплоя
build.py
start.sh
```

---

## Pages

- Home
- Treatment Categories + 6 категорий
- About Us
- Our Testimonials
- Contact Us

Тексты - `clinic/content.py`. Другой seed - через `build.py`.

---

## 📸 Screenshots

`./start.sh package` - PNG в `delivery-staging/screenshots/` и внутри zip.

---

Спасибо, что дочитал! 🐾

**xvDosha** · [github.com/xvDoshik](https://github.com/xvDoshik) · [dosha.pw](https://dosha.pw)
