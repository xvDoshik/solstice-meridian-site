#!/usr/bin/env python3
import re
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "delivery-staging"
ZIP_PATH = ROOT / "solstice-meridian-oncology-delivery.zip"
SCREENSHOTS = STAGING / "screenshots"
PREVIEW_PORT = 8765
DELIVERY_DOMAIN = "clinic.example.com"
DELIVERY_BASE = f"https://{DELIVERY_DOMAIN}"

COPY_DIRS = ("clinic", "static", "services", "_tools", "deploy")
COPY_FILES = ("build.py", "start.sh", "start.bat", ".gitignore")

INTERNAL_TOOLS = {"make_delivery.py"}

PAGES = (
    ("/", "01-home"),
    ("/about.html", "02-about"),
    ("/contact.html", "03-contact"),
    ("/testimonials.html", "04-testimonials"),
    ("/categories/index.html", "05-categories"),
    ("/categories/integrative-immunotherapy.html", "06-integrative-immunotherapy"),
    ("/categories/metabolic-restoration.html", "07-metabolic-restoration"),
    ("/categories/precision-genomic-care.html", "08-precision-genomic-care"),
    ("/categories/whole-body-detoxification.html", "09-whole-body-detoxification"),
    ("/categories/nutritional-oncology.html", "10-nutritional-oncology"),
    ("/categories/advanced-stage-support.html", "11-advanced-stage-support"),
)

SKIP_NAMES = {
    "__pycache__",
    ".DS_Store",
    "config.env",
    "contact-api.env",
}

SANITIZE = (
    (re.compile(r"clinic\.dosha\.pw"), DELIVERY_DOMAIN),
    (re.compile(r"dosha\.pw"), "example.com"),
    (re.compile(r"root@2\.27\.204\.156"), "root@YOUR_SERVER"),
    (re.compile(r"2\.27\.204\.156"), "YOUR_SERVER_IP"),
    (re.compile(r"1ab0fbed3b26d26f00099e70c1eab9a4"), ""),
    (re.compile(r"b1476d1ad0f3a82700a461cfba8f29b1"), ""),
)

TEXT_SUFFIXES = {
    ".py", ".sh", ".bat", ".ps1", ".md", ".env", ".example", ".conf",
    ".service", ".html", ".css", ".js", ".txt", ".xml", ".svg", ".json",
}


def log(msg: str) -> None:
    print(msg, flush=True)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_NAMES for part in path.parts)


def copy_tree() -> None:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir()
    for name in COPY_DIRS:
        src = ROOT / name
        if not src.exists():
            continue
        for item in src.rglob("*"):
            if should_skip(item):
                continue
            if item.name in INTERNAL_TOOLS:
                continue
            rel = item.relative_to(ROOT)
            dest = STAGING / rel
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
    for name in COPY_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, STAGING / name)


def build_root() -> None:
    subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)


def copy_public() -> None:
    src = ROOT / "public"
    dest = STAGING / "public"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def remove_secrets() -> None:
    for name in ("config.env", "contact-api.env"):
        path = STAGING / "deploy" / name
        if path.exists():
            path.unlink()


def write_examples() -> None:
    deploy = STAGING / "deploy"
    (deploy / "config.env.example").write_text(
        (deploy / "config.env.example").read_text(encoding="utf-8")
        if (deploy / "config.env.example").exists()
        else "",
        encoding="utf-8",
    )
    example = deploy / "config.env.example"
    example.write_text(
        "\n".join(
            [
                f"DOMAIN={DELIVERY_DOMAIN}",
                f"BASE_URL={DELIVERY_BASE}",
                "SSH_HOST=root@YOUR_SERVER",
                "REMOTE_DIR=/var/www/clinic",
                "PREVIEW_PORT=8080",
                "CONTACT_API_PORT=8789",
                "CLOUDFLARE_ZONE_ID=",
                "CLOUDFLARE_API_TOKEN=",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (deploy / "contact-api.env.example").write_text(
        "\n".join(
            [
                f"ALLOWED_ORIGIN={DELIVERY_BASE}",
                "CONTACT_INBOX=/var/lib/clinic-inquiries",
                "CONTACT_API_HOST=127.0.0.1",
                "CONTACT_API_PORT=8789",
                "",
            ]
        ),
        encoding="utf-8",
    )


def sanitize_file(path: Path) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
        "nginx.conf", "config.env.example", "contact-api.env.example"
    }:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    original = text
    for pattern, repl in SANITIZE:
        text = pattern.sub(repl, text)
    if text != original:
        path.write_text(text, encoding="utf-8")


def sanitize_tree() -> None:
    for path in STAGING.rglob("*"):
        if path.is_file() and not should_skip(path):
            sanitize_file(path)


def write_readme() -> None:
    (STAGING / "README.md").write_text(
        """# Solstice Meridian Oncology Institute

Static clinic website. Source generator in `clinic/`, built output in `public/`.

## Quick start

**Mac / Linux**
```bash
chmod +x start.sh
./start.sh              # local preview http://127.0.0.1:8080
./start.sh build        # rebuild public/
```

**Windows**
```bat
start.bat
start.bat build
```

## Deploy

1. Copy `deploy/config.env.example` to `deploy/config.env` and fill in your domain, SSH host, and paths.
2. Copy `deploy/contact-api.env.example` to `deploy/contact-api.env` and set `ALLOWED_ORIGIN` to your site URL.
3. Adjust `deploy/nginx.conf` for your domain and certificate paths.
4. Run `./start.sh setup` once, then `./start.sh deploy` for updates.

## Screenshots

Full-page previews of every page are in `screenshots/`.

## Structure

```
clinic/          site generator
public/          ready-to-serve static site
static/          CSS and JS sources
deploy/          nginx and service templates
services/        contact form API
_tools/          build helpers
build.py         builder entry point
start.sh         main command runner
```

## Pages

- Home
- Treatment Categories (+ 6 category pages)
- About Us
- Our Testimonials
- Contact Us
""",
        encoding="utf-8",
    )


def wait_for_port(port: int, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.3)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"preview server did not start on port {port}")


def capture_screenshots() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright", "--break-system-packages", "-q"],
            check=True,
        )
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        from playwright.sync_api import sync_playwright

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PREVIEW_PORT), "--bind", "127.0.0.1"],
        cwd=STAGING / "public",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_port(PREVIEW_PORT)
        base = f"http://127.0.0.1:{PREVIEW_PORT}"
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            for path, name in PAGES:
                log(f"screenshot {name}")
                page.goto(f"{base}{path}", wait_until="networkidle", timeout=60000)
                page.evaluate(
                    """async () => {
                        const delay = (ms) => new Promise((r) => setTimeout(r, ms));
                        const maxY = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
                        for (let y = 0; y <= maxY; y += Math.max(400, window.innerHeight)) {
                            window.scrollTo(0, y);
                            await delay(120);
                        }
                        window.scrollTo(0, 0);
                        await delay(200);
                        const imgs = [...document.images];
                        await Promise.all(imgs.map((img) => {
                            if (img.complete) return Promise.resolve();
                            return new Promise((resolve) => {
                                img.addEventListener("load", resolve, { once: true });
                                img.addEventListener("error", resolve, { once: true });
                            });
                        }));
                    }"""
                )
                page.wait_for_timeout(300)
                page.screenshot(path=str(SCREENSHOTS / f"{name}.png"), full_page=True)
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=5)


def create_zip() -> None:
    root_name = "solstice-meridian-oncology"
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(STAGING.rglob("*")):
            if path.is_file():
                arc = Path(root_name) / path.relative_to(STAGING)
                zf.write(path, arc.as_posix())


def main() -> None:
    log("copy sources")
    copy_tree()
    log("build site")
    build_root()
    log("copy public output")
    copy_public()
    remove_secrets()
    write_examples()
    sanitize_tree()
    write_readme()
    log("capture screenshots")
    capture_screenshots()
    log("create zip")
    create_zip()
    size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    log(f"done: {ZIP_PATH} ({size_mb:.1f} MB)")
    log(f"screenshots: {SCREENSHOTS}")


if __name__ == "__main__":
    main()
