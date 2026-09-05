import hashlib
import re
import ssl
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
SKIP = ("logo", "favicon", "icon", "avatar", "sprite", "emoji", "placeholder")
SIZE_SUFFIX = re.compile(r"-\d+x\d+$", re.I)
SITES = (
    "https://www.burzynskiclinic.com/",
    "https://www.hope4cancer.com/",
    "https://www.oasisofhope.com/",
    "https://verita-life.com/",
    "https://drsalvadorvargas.com/",
    "https://www.immunotherapyinstitute.com/",
    "https://www.anotherway.com/",
    "https://www.holisticcare.com/",
    "https://www.cancer.gov/",
    "https://www.cancerclinicsmx.com/",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        for key in ("src", "data-src", "data-lazy-src", "href"):
            val = data.get(key)
            if val:
                self.links.add(val)
        srcset = data.get("srcset")
        if srcset:
            for part in srcset.split(","):
                url = part.strip().split(" ")[0]
                if url:
                    self.links.add(url)


def fetch_html(url: str, ctx: ssl.SSLContext) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def collect_urls(base: str, ctx: ssl.SSLContext) -> set[str]:
    found: set[str] = set()
    try:
        html = fetch_html(base, ctx)
    except Exception:
        return found
    parser = LinkParser()
    parser.feed(html)
    for link in parser.links:
        full = urllib.parse.urljoin(base, link)
        path = urllib.parse.urlparse(full).path.lower()
        if any(path.endswith(ext) for ext in IMG_EXT):
            found.add(full.split("?")[0])
    for path in ("/about/", "/about-us/", "/treatments/", "/our-treatments/", "/gallery/", "/facilities/"):
        page = urllib.parse.urljoin(base, path)
        try:
            sub = fetch_html(page, ctx)
        except Exception:
            continue
        p = LinkParser()
        p.feed(sub)
        for link in p.links:
            full = urllib.parse.urljoin(page, link)
            pth = urllib.parse.urlparse(full).path.lower()
            if any(pth.endswith(ext) for ext in IMG_EXT):
                found.add(full.split("?")[0])
    return found


def stem_key(name: str) -> str:
    stem = Path(name).stem.lower()
    return SIZE_SUFFIX.sub("", stem)


def download(url: str, dest: Path, ctx: ssl.SSLContext) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
            data = resp.read()
        if len(data) < 12000:
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def run(target_root: Path) -> int:
    ctx = ssl.create_default_context()
    target_root.mkdir(parents=True, exist_ok=True)
    seen_stems: set[str] = set()
    seen_hash: set[str] = set()
    saved = 0
    for base in SITES:
        host = urllib.parse.urlparse(base).netloc.replace("www.", "")
        out_dir = target_root / host
        out_dir.mkdir(parents=True, exist_ok=True)
        urls = collect_urls(base, ctx)
        for url in sorted(urls):
            name = Path(urllib.parse.urlparse(url).path).name.lower()
            if not name or any(x in name for x in SKIP):
                continue
            key = stem_key(name)
            if key in seen_stems:
                continue
            dest = out_dir / name
            if download(url, dest, ctx):
                digest = hashlib.md5(dest.read_bytes()).hexdigest()
                if digest in seen_hash:
                    dest.unlink(missing_ok=True)
                    continue
                seen_stems.add(key)
                seen_hash.add(digest)
                saved += 1
    return saved


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2] / "sites" / "fetched"
    print(run(root))
