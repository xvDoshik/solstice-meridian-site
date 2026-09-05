import random


class RandomCopyGenerator:
    OPENERS = (
        "Our multidisciplinary team coordinates",
        "The institute maintains",
        "Each patient pathway begins with",
        "Clinical coordinators review",
        "Integrated diagnostics support",
        "Therapeutic planning incorporates",
    )
    MIDDLE = (
        "personalized biomarker mapping",
        "continuous immune modulation",
        "structured nutritional protocols",
        "precision-guided infusion schedules",
        "whole-body metabolic assessment",
        "adaptive monitoring checkpoints",
    )
    CLOSERS = (
        "to align treatment intensity with daily resilience.",
        "while preserving comfort and clarity at every stage.",
        "so families receive transparent progress updates.",
        "with concierge navigation through each visit.",
        "and structured follow-up between onsite sessions.",
        "within a calm, patient-centered environment.",
    )
    HEADLINES = (
        "Restoring balance through integrative oncology",
        "Advanced care pathways for complex diagnoses",
        "Compassionate support from first consultation",
        "Evidence-informed therapies under one roof",
        "Holistic recovery planning for every guest",
    )
    NAMES = (
        "Elena Morales", "James Whitfield", "Priya Nair", "Robert Chen",
        "Sofia Andersson", "Michael Okafor", "Laura Bennett", "Daniel Ruiz",
    )
    CITIES = (
        "San Diego, CA", "Austin, TX", "Vancouver, BC", "Phoenix, AZ",
        "Denver, CO", "Portland, OR", "Calgary, AB", "Miami, FL",
    )

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def paragraph(self) -> str:
        return (
            f"{self.rng.choice(self.OPENERS)} {self.rng.choice(self.MIDDLE)} "
            f"{self.rng.choice(self.CLOSERS)}"
        )

    def paragraphs(self, count: int) -> tuple[str, ...]:
        return tuple(self.paragraph() for _ in range(count))

    def headline(self) -> str:
        return self.rng.choice(self.HEADLINES)

    def summary(self) -> str:
        return self.paragraph()

    def category_title(self, base: str) -> str:
        suffix = self.rng.choice(("Program", "Pathway", "Protocol", "Center", "Suite"))
        return f"{base} {suffix}"

    def testimonial(self, image: str) -> dict[str, str]:
        return {
            "author": self.rng.choice(self.NAMES),
            "origin": self.rng.choice(self.CITIES),
            "headline": self.headline(),
            "quote": " ".join(self.paragraphs(2)),
            "image": image,
        }
