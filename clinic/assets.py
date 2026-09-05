import hashlib
import re
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


class AssetHarvester:
    IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
    SKIP_PARTS = ("logo", "favicon", "icon", "avatar", "sprite", "emoji", "placeholder", "banner-ad")
    SIZE_SUFFIX = re.compile(r"-\d+x\d+$", re.I)
    MIN_BYTES = 12000

    def __init__(self, sources: list[Path], target: Path) -> None:
        self.sources = sources
        self.target = target

    def _stem_key(self, path: Path) -> str:
        return self.SIZE_SUFFIX.sub("", path.stem.lower())

    def _collect(self) -> list[Path]:
        best: dict[str, Path] = {}
        for root in self.sources:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in self.IMAGE_EXT:
                    continue
                name = path.name.lower()
                if any(x in name for x in self.SKIP_PARTS):
                    continue
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size < self.MIN_BYTES:
                    continue
                key = self._stem_key(path)
                prev = best.get(key)
                if prev is None or size > prev.stat().st_size:
                    best[key] = path
        return sorted(best.values(), key=lambda p: p.stat().st_size, reverse=True)

    def harvest(self, limit: int = 48) -> list[str]:
        self.target.mkdir(parents=True, exist_ok=True)
        names: list[str] = []
        seen_hash: set[str] = set()
        for path in self._collect():
            digest = hashlib.md5(path.read_bytes()).hexdigest()
            if digest in seen_hash:
                continue
            seen_hash.add(digest)
            dest_name = f"asset_{len(names) + 1:02d}{path.suffix.lower()}"
            dest = self.target / dest_name
            shutil.copy2(path, dest)
            names.append(dest_name)
            if len(names) >= limit:
                break
        return names


class ImageNormalizer:
    JPEG_QUALITY = 88

    def __init__(self, assets_dir: Path) -> None:
        self.assets_dir = assets_dir

    def normalize_all(self) -> None:
        if Image is None:
            return
        for path in sorted(self.assets_dir.iterdir()):
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            try:
                with Image.open(path) as img:
                    if ext in {".jpg", ".jpeg"}:
                        img.convert("RGB").save(
                            path, "JPEG", quality=self.JPEG_QUALITY, optimize=True
                        )
                    elif ext == ".png":
                        img.save(path, "PNG", optimize=True)
                    else:
                        img.save(path, "WEBP", quality=self.JPEG_QUALITY, method=6)
            except OSError:
                continue


class AssetVersion:
    @staticmethod
    def compute(assets_dir: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(assets_dir.iterdir()):
            if path.is_file():
                digest.update(path.name.encode())
                digest.update(path.read_bytes())
        return digest.hexdigest()[:12]


class FaviconBuilder:
    BRAND = "#0f6e8c"

    def __init__(self, root: Path, public: Path) -> None:
        self.root = root
        self.public = public

    def build(self) -> None:
        svg = self.root / "static" / "favicon.svg"
        if svg.exists():
            shutil.copy2(svg, self.public / "favicon.svg")
        if Image is None or ImageDraw is None:
            if svg.exists():
                shutil.copy2(svg, self.public / "favicon.ico")
            return
        img = Image.new("RGB", (32, 32), self.BRAND)
        draw = ImageDraw.Draw(img)
        draw.text((16, 15), "SM", fill="#ffffff", anchor="mm")
        img.save(self.public / "favicon-32.png", format="PNG", optimize=True)
        img.save(
            self.public / "favicon.ico",
            format="ICO",
            sizes=[(16, 16), (32, 32)],
        )


class ImageAllocator:
    SLOTS = (
        "hero",
        "home_split",
        "home_quote",
        "about_a",
        "about_b",
        "contact",
        "card_0",
        "card_1",
        "card_2",
        "card_3",
        "card_4",
        "card_5",
        "hero_0",
        "hero_1",
        "hero_2",
        "hero_3",
        "hero_4",
        "hero_5",
        "testimonial_0",
        "testimonial_1",
        "testimonial_2",
        "testimonial_3",
        "testimonial_4",
        "testimonial_5",
        "og_home",
        "og_about",
        "og_contact",
        "og_testimonials",
        "og_categories",
        "og_cat_0",
        "og_cat_1",
        "og_cat_2",
        "og_cat_3",
        "og_cat_4",
        "og_cat_5",
    )

    def __init__(self, images: list[str]) -> None:
        if len(images) < len(self.SLOTS):
            raise ValueError(f"need {len(self.SLOTS)} images, got {len(images)}")
        self._map = dict(zip(self.SLOTS, images))

    def get(self, slot: str) -> str:
        return self._map[slot]

    def cards(self) -> tuple[str, ...]:
        return tuple(self.get(f"card_{i}") for i in range(6))

    def category_heroes(self) -> tuple[str, ...]:
        return tuple(self.get(f"hero_{i}") for i in range(6))

    def category_og(self) -> tuple[str, ...]:
        return tuple(self.get(f"og_cat_{i}") for i in range(6))

    def testimonials(self) -> tuple[str, ...]:
        return tuple(self.get(f"testimonial_{i}") for i in range(6))


class PageImageGuard:
    MAIN_RE = re.compile(
        r'(?:src="|background-image:url\(\'(?:/?assets/)?)(asset_\d+\.\w+)'
    )
    OG_RE = re.compile(
        r'property="og:image" content="[^"]*/(asset_\d+\.\w+)"'
    )

    @classmethod
    def _main_assets(cls, html: str) -> list[str]:
        chunk = html.split("<main>", 1)[-1].split("</main>", 1)[0]
        return cls.MAIN_RE.findall(chunk)

    @classmethod
    def _og_asset(cls, html: str) -> str | None:
        found = cls.OG_RE.findall(html)
        return found[0] if found else None

    @classmethod
    def assert_unique(cls, html: str, page: str) -> None:
        main = cls._main_assets(html)
        seen: set[str] = set()
        for asset in main:
            if asset in seen:
                raise ValueError(f"duplicate {asset} in body on {page}")
            seen.add(asset)
        og = cls._og_asset(html)
        if og and og in seen:
            raise ValueError(f"og image {og} repeats body on {page}")
