from clinic.domain import SiteMap, TreatmentCategory
from clinic.layout import PageRenderer, SectionBuilder
from clinic.routes import Routes
from clinic.seo import PageSeo


class HomePageRenderer(PageRenderer):
    def title(self) -> str:
        return "Home"

    def seo_page(self) -> PageSeo:
        return PageSeo(
            title="Integrative Cancer Care",
            description=f"{self.profile.name}. {self.profile.tagline} Personalized oncology pathways, testimonials, and consultation booking.",
            path=Routes.HOME,
            image=f"assets/{self.site.images.og.home}",
        )

    def body(self) -> str:
        img = self.site.images
        cards = [
            (c.title, c.summary, c.image, Routes.category(c.slug), c.title)
            for c in self.site.categories[:6]
        ]
        stats = """
<section class="stats">
  <div class="wrap stats-grid">
    <div><strong>40+</strong><span>Integrated modalities</span></div>
    <div><strong>24/7</strong><span>Clinical coordination</span></div>
    <div><strong>12</strong><span>Specialist departments</span></div>
    <div><strong>Global</strong><span>Patient guest services</span></div>
  </div>
</section>"""
        testimonial = self.site.testimonials[0]
        quote_block = f"""
<section class="quote-strip">
  <div class="wrap">
    <p class="quote-compact">&ldquo;{self.esc.text(testimonial.headline)}&rdquo;
      <span class="quote-compact-meta">{self.esc.text(testimonial.author)} · {self.esc.text(testimonial.origin)} · <a href="{Routes.TESTIMONIALS}">Reviews</a></span>
    </p>
  </div>
</section>"""
        return (
            SectionBuilder.hero(
                self.profile.tagline,
                self.site.categories[0].body[0],
                img.hero,
                f"{self.profile.short_name} integrative oncology campus",
                Routes.CONTACT,
                "Request a private consultation",
            )
            + stats
            + SectionBuilder.cards("Treatment Categories", cards)
            + SectionBuilder.split(
                "Patient-first integrative oncology",
                self.site.categories[1].body[:2],
                img.home_split,
                "Clinical team consultation area",
            )
            + quote_block
        )


class AboutPageRenderer(PageRenderer):
    def title(self) -> str:
        return "About Us"

    def seo_page(self) -> PageSeo:
        return PageSeo(
            title="About Us",
            description=f"Learn about {self.profile.name}, our mission, clinical philosophy, and integrative oncology institute history since {self.profile.founded}.",
            path=Routes.ABOUT,
            image=f"assets/{self.site.images.og.about}",
        )

    def breadcrumbs(self) -> list[tuple[str, str]]:
        return [("Home", Routes.HOME), ("About Us", Routes.ABOUT)]

    def body(self) -> str:
        p = self.site.categories[0].body
        team_img, clinic_img = self.site.images.about
        return f"""
<section class="page-hero"><div class="wrap"><h1>About Us</h1><p class="lead">{self.esc.text(self.profile.tagline)}</p></div></section>
{SectionBuilder.split("Our mission", p[:3], team_img, "Medical team at Solstice Meridian")}
{SectionBuilder.split("Clinical philosophy", p[1:4], clinic_img, "Integrative oncology treatment facility", reverse=True)}
<section class="section muted"><div class="wrap prose">
  <h2>Institute overview</h2>
  <p>Founded in {self.profile.founded}, {self.esc.text(self.profile.name)} unifies diagnostic review, integrative therapy planning, and longitudinal guest support within a single coastal campus.</p>
  <p>{self.esc.text(p[0])}</p>
  <p>{self.esc.text(p[1])}</p>
</div></section>"""


class ContactPageRenderer(PageRenderer):
    def title(self) -> str:
        return "Contact Us"

    def seo_page(self) -> PageSeo:
        return PageSeo(
            title="Contact Us",
            description=f"Contact {self.profile.name} for consultations, medical records transfer, and travel coordination. Phone {self.profile.phone}.",
            path=Routes.CONTACT,
            image=f"assets/{self.site.images.og.contact}",
        )

    def breadcrumbs(self) -> list[tuple[str, str]]:
        return [("Home", Routes.HOME), ("Contact Us", Routes.CONTACT)]

    def body(self) -> str:
        return f"""
<section class="page-hero"><div class="wrap"><h1>Contact Us</h1><p class="lead">Reach our intake team for scheduling, records transfer, and travel coordination.</p></div></section>
<section class="section"><div class="wrap contact-grid">
  <form class="contact-form" id="contact-form" method="post" action="/api/contact" novalidate>
    <input type="text" name="company" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label>Full name<input type="text" name="name" required maxlength="120" autocomplete="name"></label>
    <label>Email<input type="email" name="email" required maxlength="254" autocomplete="email"></label>
    <label>Phone<input type="tel" name="phone" maxlength="40" autocomplete="tel"></label>
    <label>Primary concern<textarea name="message" rows="5" required maxlength="5000"></textarea></label>
    <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
    <button class="btn btn-primary" type="submit">Send inquiry</button>
  </form>
  <aside class="contact-card">
    <h2>Visit the institute</h2>
    <p><strong>Address</strong><br>{self.esc.text(self.profile.address)}<br>{self.esc.text(self.profile.city)}</p>
    <p><strong>Phone</strong><br><a href="tel:{self.esc.attr(self.profile.phone.replace(' ', ''))}">{self.esc.text(self.profile.phone)}</a></p>
    <p><strong>Email</strong><br><a href="mailto:{self.esc.attr(self.profile.email)}">{self.esc.text(self.profile.email)}</a></p>
    <p><strong>Hours</strong><br>{self.esc.text(self.profile.hours)}</p>
    <img src="{self.asset(self.site.images.contact)}" alt="Clinic reception and guest area" loading="lazy">
  </aside>
</div></section>"""


class TestimonialsPageRenderer(PageRenderer):
    def title(self) -> str:
        return "Our Testimonials"

    def seo_page(self) -> PageSeo:
        return PageSeo(
            title="Our Testimonials",
            description=f"Patient testimonials and recovery stories from guests treated at {self.profile.name}.",
            path=Routes.TESTIMONIALS,
            image=f"assets/{self.site.images.og.testimonials}",
        )

    def breadcrumbs(self) -> list[tuple[str, str]]:
        return [("Home", Routes.HOME), ("Our Testimonials", Routes.TESTIMONIALS)]

    def body(self) -> str:
        items = "".join(
            f"""<article class="testimonial">
  <img src="{self.asset(t.image)}" alt="{self.esc.text(t.author)} patient story" loading="lazy">
  <div>
    <h3>{self.esc.text(t.headline)}</h3>
    <p class="quote">&ldquo;{self.esc.text(t.quote)}&rdquo;</p>
    <p class="quote-meta">{self.esc.text(t.author)} · {self.esc.text(t.origin)}</p>
  </div>
</article>"""
            for t in self.site.testimonials
        )
        return f"""
<section class="page-hero"><div class="wrap"><h1>Our Testimonials</h1><p class="lead">Stories shared by guests and families who traveled to our institute for integrative oncology care.</p></div></section>
<section class="section"><div class="wrap testimonial-stack">{items}</div></section>"""


class CategoriesIndexRenderer(PageRenderer):
    def title(self) -> str:
        return "Treatment Categories"

    def seo_page(self) -> PageSeo:
        return PageSeo(
            title="Treatment Categories",
            description=f"Browse integrative oncology treatment categories at {self.profile.name}: immunotherapy, metabolic care, genomic programs, and more.",
            path=Routes.CATEGORIES,
            image=f"assets/{self.site.images.og.categories}",
        )

    def breadcrumbs(self) -> list[tuple[str, str]]:
        return [("Home", Routes.HOME), ("Categories", Routes.CATEGORIES)]

    def body(self) -> str:
        rows = "".join(
            f"""<article class="category-row">
  <img src="{self.asset(c.image)}" alt="{self.esc.text(c.title)}" loading="lazy">
  <div>
    <h2>{self.esc.text(c.title)}</h2>
    <p>{self.esc.text(c.summary)}</p>
    <a href="{Routes.category(c.slug)}">View category details</a>
  </div>
</article>"""
            for c in self.site.categories
        )
        return f"""
<section class="page-hero"><div class="wrap"><h1>Treatment Categories</h1><p class="lead">Explore the primary clinical pathways offered across our integrative oncology departments.</p></div></section>
<section class="section"><div class="wrap category-list">{rows}</div></section>"""


class CategoryPageRenderer(PageRenderer):
    def __init__(self, site: SiteMap, seo, category: TreatmentCategory) -> None:
        super().__init__(site, seo)
        self.category = category

    def title(self) -> str:
        return self.category.title

    def seo_page(self) -> PageSeo:
        return PageSeo(
            title=self.category.title,
            description=self.category.summary,
            path=Routes.category(self.category.slug),
            image=f"assets/{self.category.og_image}",
            type="article",
        )

    def breadcrumbs(self) -> list[tuple[str, str]]:
        return [
            ("Home", Routes.HOME),
            ("Categories", Routes.CATEGORIES),
            (self.category.title, Routes.category(self.category.slug)),
        ]

    def body(self) -> str:
        paragraphs = "".join(f"<p>{self.esc.text(p)}</p>" for p in self.category.body)
        return f"""
<section class="page-hero category-hero" style="background-image:url('{self.esc.attr(self.asset(self.category.hero_image))}')">
  <div class="hero-overlay"></div>
  <div class="wrap"><h1>{self.esc.text(self.category.title)}</h1><p class="lead">{self.esc.text(self.category.summary)}</p></div>
</section>
<section class="section"><div class="wrap prose">{paragraphs}</div></section>"""
