import os
from pathlib import Path

from clinic.assets import (
    AssetHarvester,
    AssetVersion,
    FaviconBuilder,
    ImageAllocator,
    ImageNormalizer,
    PageImageGuard,
)
from clinic.routes import Routes
from clinic.content import RandomCopyGenerator
from clinic.domain import ClinicProfile, NavItem, OgImages, SiteImages, SiteMap, Testimonial, TreatmentCategory
from clinic.pages import (
    AboutPageRenderer,
    CategoriesIndexRenderer,
    CategoryPageRenderer,
    ContactPageRenderer,
    HomePageRenderer,
    TestimonialsPageRenderer,
)
from clinic.seo import SeoEngine


class ConfigLoader:
    @staticmethod
    def load(root: Path) -> dict[str, str]:
        env_path = root / "deploy" / "config.env"
        values: dict[str, str] = {}
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                values[key.strip()] = val.strip()
        values.setdefault("BASE_URL", os.environ.get("BASE_URL", "https://clinic.dosha.pw"))
        return values


class SiteFactory:
    CATEGORY_BASES = (
        "Integrative Immunotherapy",
        "Metabolic Restoration",
        "Precision Genomic Care",
        "Whole-Body Detoxification",
        "Nutritional Oncology",
        "Advanced Stage Support",
    )

    def __init__(self, copy: RandomCopyGenerator, allocator: ImageAllocator) -> None:
        self.copy = copy
        self.alloc = allocator

    def build(self) -> SiteMap:
        profile = ClinicProfile(
            name="Solstice Meridian Oncology Institute",
            short_name="Solstice Meridian",
            tagline=self.copy.headline(),
            founded=1989,
            email="intake@solsticemeridian.org",
            phone="+1 (619) 555-0148",
            address="880 Harbor Integrative Medical Campus, Suite 400",
            city="Playas de Tijuana, Baja California, Mexico",
            hours="Mon–Sat 8:00–18:00 · Intake desk 24/7",
        )
        nav = (
            NavItem("Home", Routes.HOME),
            NavItem("Services", Routes.CATEGORIES),
            NavItem("About", Routes.ABOUT),
            NavItem("Reviews", Routes.TESTIMONIALS),
            NavItem("Contact", Routes.CONTACT),
        )
        cards = self.alloc.cards()
        heroes = self.alloc.category_heroes()
        og_cats = self.alloc.category_og()
        categories = tuple(
            self._category(i, base, cards[i], heroes[i], og_cats[i])
            for i, base in enumerate(self.CATEGORY_BASES)
        )
        testimonial_images = self.alloc.testimonials()
        testimonials = tuple(self._testimonial(i, testimonial_images[i]) for i in range(6))
        images = SiteImages(
            hero=self.alloc.get("hero"),
            home_split=self.alloc.get("home_split"),
            home_quote=self.alloc.get("home_quote"),
            about=(self.alloc.get("about_a"), self.alloc.get("about_b")),
            contact=self.alloc.get("contact"),
            og=OgImages(
                home=self.alloc.get("og_home"),
                about=self.alloc.get("og_about"),
                contact=self.alloc.get("og_contact"),
                testimonials=self.alloc.get("og_testimonials"),
                categories=self.alloc.get("og_categories"),
            ),
        )
        return SiteMap(
            profile=profile,
            images=images,
            nav=nav,
            categories=categories,
            testimonials=testimonials,
        )

    def _category(self, index: int, base: str, card: str, hero: str, og: str) -> TreatmentCategory:
        slug = base.lower().replace(" ", "-")
        return TreatmentCategory(
            slug=slug,
            title=self.copy.category_title(base),
            summary=self.copy.summary(),
            body=self.copy.paragraphs(4),
            image=card,
            hero_image=hero,
            og_image=og,
        )

    def _testimonial(self, index: int, image: str) -> Testimonial:
        data = self.copy.testimonial(image)
        return Testimonial(**data)


class SiteAssembler:
    RENDERERS = {
        "index.html": HomePageRenderer,
        "about.html": AboutPageRenderer,
        "contact.html": ContactPageRenderer,
        "testimonials.html": TestimonialsPageRenderer,
        "categories/index.html": CategoriesIndexRenderer,
    }

    def __init__(self, root: Path, dump_roots: list[Path]) -> None:
        self.root = root
        self.public = root / "public"
        self.dump_roots = dump_roots
        cfg = ConfigLoader.load(root)
        self.seo = SeoEngine(cfg["BASE_URL"], "Solstice Meridian Oncology Institute")

    def run(self, seed: int = 42) -> dict[str, int]:
        assets_dir = self.public / "assets"
        images = AssetHarvester(self.dump_roots, assets_dir).harvest(limit=40)
        ImageNormalizer(assets_dir).normalize_all()
        css_src = self.root / "static" / "site.css"
        js_src = self.root / "static" / "site.js"
        if css_src.exists():
            (assets_dir / "site.css").write_text(css_src.read_text(encoding="utf-8"), encoding="utf-8")
        if js_src.exists():
            (assets_dir / "site.js").write_text(js_src.read_text(encoding="utf-8"), encoding="utf-8")
        Routes.set_asset_version(AssetVersion.compute(assets_dir))
        FaviconBuilder(self.root, self.public).build()
        allocator = ImageAllocator(images)
        copy = RandomCopyGenerator(seed)
        site = SiteFactory(copy, allocator).build()
        paths: list[str] = []
        counts: dict[str, int] = {"pages": 0, "assets": len(images)}
        for rel, renderer_cls in self.RENDERERS.items():
            content = renderer_cls(site, self.seo).render()
            PageImageGuard.assert_unique(content, rel)
            self._write(rel, content)
            paths.append(Routes.clean(rel))
            counts["pages"] += 1
        for category in site.categories:
            rel = f"categories/{category.slug}.html"
            content = CategoryPageRenderer(site, self.seo, category).render()
            PageImageGuard.assert_unique(content, rel)
            self._write(rel, content)
            paths.append(Routes.category(category.slug))
            counts["pages"] += 1
        self._write("robots.txt", self.seo.robots())
        self._write("sitemap.xml", self.seo.sitemap(paths))
        counts["pages"] += 2
        return counts

    def _write(self, rel: str, content: str) -> None:
        path = self.public / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
