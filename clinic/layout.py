from abc import ABC, abstractmethod

from clinic.domain import ClinicProfile, SiteMap
from clinic.routes import Routes
from clinic.security import HtmlEscaper
from clinic.seo import PageSeo, SeoEngine


class PageRenderer(ABC):
    def __init__(self, site: SiteMap, seo: SeoEngine) -> None:
        self.site = site
        self.seo = seo
        self.esc = HtmlEscaper

    @property
    def profile(self) -> ClinicProfile:
        return self.site.profile

    def href(self, path: str) -> str:
        if path.startswith("/"):
            return self.esc.attr(path)
        return self.esc.attr(Routes.clean(path))

    def asset(self, name: str) -> str:
        return Routes.asset(name)

    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def seo_page(self) -> PageSeo:
        raise NotImplementedError

    def breadcrumbs(self) -> list[tuple[str, str]] | None:
        return None

    @abstractmethod
    def body(self) -> str:
        raise NotImplementedError

    def render(self) -> str:
        return self._shell(self.title(), self.body(), self.seo_page())

    def _nav_links(self) -> str:
        current = self.seo_page().path
        links = []
        for item in self.site.nav:
            active = ' aria-current="page"' if item.href == current else ""
            links.append(
                f'<a href="{self.href(item.href)}" class="nav-link"{active}>{self.esc.text(item.label)}</a>'
            )
        return "".join(links)

    def _shell(self, title: str, content: str, meta: PageSeo) -> str:
        nav = self._nav_links()
        crumbs = self.breadcrumbs()
        crumb_html = ""
        if crumbs:
            items = "".join(
                f'<li><a href="{self.href(path)}">{self.esc.text(label)}</a></li>'
                for label, path in crumbs
            )
            crumb_html = f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{items}</ol></nav>'
            extra_ld = self.seo.breadcrumb_json(crumbs)
        else:
            extra_ld = ""
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{self.esc.text(title)} | {self.esc.text(self.profile.short_name)}</title>
{self.seo.head(meta)}
{self.seo.organization_json(self.profile)}
{extra_ld}
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon-32.png">
<link rel="stylesheet" href="{self.asset('site.css')}">
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{Routes.HOME}">
      <span class="brand-mark" aria-hidden="true">SM</span>
      <span class="brand-name">{self.esc.text(self.profile.short_name)}</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">
      <span class="nav-toggle-bar"></span>
      <span class="nav-toggle-bar"></span>
      <span class="nav-toggle-bar"></span>
    </button>
    <div class="header-menu" id="site-nav">
      <nav class="nav" aria-label="Primary">{nav}</nav>
      <a class="btn btn-primary header-cta" href="{Routes.CONTACT}">Book</a>
    </div>
  </div>
  <div class="nav-backdrop" aria-hidden="true"></div>
</header>
<main>{crumb_html}{content}</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <strong>{self.esc.text(self.profile.name)}</strong>
      <p>{self.esc.text(self.profile.tagline)}</p>
    </div>
    <div>
      <p>{self.esc.text(self.profile.address)}</p>
      <p>{self.esc.text(self.profile.city)}</p>
    </div>
    <div>
      <p>{self.esc.text(self.profile.phone)}</p>
      <p>{self.esc.text(self.profile.email)}</p>
      <p>{self.esc.text(self.profile.hours)}</p>
    </div>
  </div>
</footer>
<script src="{self.asset('site.js')}" defer></script>
</body>
</html>"""


class SectionBuilder:
    esc = HtmlEscaper

    @classmethod
    def hero(cls, title: str, subtitle: str, image: str, alt: str, cta_href: str, cta_label: str) -> str:
        return f"""
<section class="hero" style="background-image:url('{cls.esc.attr(Routes.asset(image))}')" role="img" aria-label="{cls.esc.attr(alt)}">
  <div class="hero-overlay"></div>
  <div class="wrap hero-content">
    <p class="eyebrow">Integrative Oncology Institute</p>
    <h1>{cls.esc.text(title)}</h1>
    <p class="lead">{cls.esc.text(subtitle)}</p>
    <a class="btn btn-light" href="{cls.esc.attr(cta_href)}">{cls.esc.text(cta_label)}</a>
  </div>
</section>"""

    @classmethod
    def split(cls, title: str, paragraphs: tuple[str, ...], image: str, alt: str, reverse: bool = False) -> str:
        text = "".join(f"<p>{cls.esc.text(p)}</p>" for p in paragraphs)
        order = "split reverse" if reverse else "split"
        return f"""
<section class="{order}">
  <div class="wrap split-grid">
    <div class="split-copy">
      <h2>{cls.esc.text(title)}</h2>
      {text}
    </div>
    <figure class="split-media"><img src="{cls.esc.attr(Routes.asset(image))}" alt="{cls.esc.text(alt)}" loading="lazy"></figure>
  </div>
</section>"""

    @classmethod
    def cards(cls, title: str, items: list[tuple[str, str, str, str, str]]) -> str:
        cards = "".join(
            f"""<article class="card">
  <img src="{cls.esc.attr(Routes.asset(img))}" alt="{cls.esc.text(alt)}" loading="lazy">
  <div class="card-body">
    <h3>{cls.esc.text(name)}</h3>
    <p>{cls.esc.text(summary)}</p>
    <a href="{cls.esc.attr(href)}">Explore pathway</a>
  </div>
</article>"""
            for name, summary, img, href, alt in items
        )
        return f"""
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>{cls.esc.text(title)}</h2></div>
    <div class="card-grid">{cards}</div>
  </div>
</section>"""
