from dataclasses import dataclass
import html
import json
from xml.etree.ElementTree import Element, SubElement, tostring


from clinic.routes import Routes
from clinic.security import JsonLdEncoder


@dataclass(frozen=True)
class PageSeo:
    title: str
    description: str
    path: str
    image: str = "assets/asset_04.jpg"
    type: str = "website"


class SeoEngine:
    def __init__(self, base_url: str, site_name: str, locale: str = "en_US") -> None:
        self.base_url = base_url.rstrip("/")
        self.site_name = site_name
        self.locale = locale

    def url(self, path: str) -> str:
        clean = path if path.startswith("/") else Routes.clean(path)
        if clean == Routes.HOME:
            return f"{self.base_url}/"
        return f"{self.base_url}{clean}"

    def head(self, page: PageSeo) -> str:
        title = html.escape(f"{page.title} | {self.site_name}")
        desc = html.escape(page.description[:320])
        canonical = html.escape(self.url(page.path))
        asset_name = page.image.removeprefix("assets/")
        og_image = html.escape(f"{self.base_url}{Routes.asset(asset_name)}")
        og_type = html.escape(page.type)
        return f"""
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0f6e8c">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<meta property="og:site_name" content="{html.escape(self.site_name)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="{self.locale}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_image}">"""

    def organization_json(self, profile) -> str:
        payload = {
            "@context": "https://schema.org",
            "@type": "MedicalClinic",
            "name": profile.name,
            "description": profile.tagline,
            "url": self.base_url,
            "email": profile.email,
            "telephone": profile.phone,
            "foundingDate": str(profile.founded),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": profile.address,
                "addressLocality": profile.city,
                "addressCountry": "MX",
            },
            "openingHours": profile.hours,
            "medicalSpecialty": "Oncologic",
        }
        return JsonLdEncoder.script(payload)

    def breadcrumb_json(self, items: list[tuple[str, str]]) -> str:
        elements = []
        for idx, (name, path) in enumerate(items, 1):
            elements.append({
                "@type": "ListItem",
                "position": idx,
                "name": name,
                "item": self.url(path),
            })
        payload = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": elements,
        }
        return JsonLdEncoder.script(payload)

    def sitemap(self, paths: list[str]) -> str:
        urlset = Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        for path in paths:
            node = SubElement(urlset, "url")
            SubElement(node, "loc").text = self.url(path)
            SubElement(node, "changefreq").text = "weekly"
            SubElement(node, "priority").text = "0.8" if path == Routes.HOME else "0.6"
        body = tostring(urlset, encoding="unicode")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + body

    def robots(self) -> str:
        return f"User-agent: *\nAllow: /\nSitemap: {self.url('sitemap.xml')}\n"
