from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClinicProfile:
    name: str
    short_name: str
    tagline: str
    founded: int
    email: str
    phone: str
    address: str
    city: str
    hours: str


@dataclass(frozen=True)
class TreatmentCategory:
    slug: str
    title: str
    summary: str
    body: tuple[str, ...]
    image: str
    hero_image: str
    og_image: str


@dataclass(frozen=True)
class OgImages:
    home: str
    about: str
    contact: str
    testimonials: str
    categories: str


@dataclass(frozen=True)
class SiteImages:
    hero: str
    home_split: str
    home_quote: str
    about: tuple[str, str]
    contact: str
    og: OgImages


@dataclass(frozen=True)
class Testimonial:
    author: str
    origin: str
    headline: str
    quote: str
    image: str


@dataclass(frozen=True)
class NavItem:
    label: str
    href: str


@dataclass
class SiteMap:
    profile: ClinicProfile
    images: SiteImages
    nav: tuple[NavItem, ...] = field(default_factory=tuple)
    categories: tuple[TreatmentCategory, ...] = field(default_factory=tuple)
    testimonials: tuple[Testimonial, ...] = field(default_factory=tuple)
