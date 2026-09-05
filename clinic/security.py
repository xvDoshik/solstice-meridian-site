import html
import json
import re


class HtmlEscaper:
    @staticmethod
    def text(value: str) -> str:
        return html.escape(str(value), quote=False)

    @staticmethod
    def attr(value: str) -> str:
        return html.escape(str(value), quote=True)


class JsonLdEncoder:
    @staticmethod
    def script(payload: dict) -> str:
        raw = json.dumps(payload, ensure_ascii=False)
        raw = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        return f'<script type="application/ld+json">{raw}</script>'


class InputSanitizer:
    TAG_RE = re.compile(r"<[^>]+>")
    CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
    EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
    PHONE_RE = re.compile(r"^[\d\s+\-().]{0,40}$")

    @classmethod
    def plain_text(cls, value: str, limit: int) -> str:
        cleaned = cls.TAG_RE.sub("", str(value or ""))
        cleaned = cls.CONTROL_RE.sub("", cleaned)
        cleaned = cleaned.strip()
        if len(cleaned) > limit:
            raise ValueError("too long")
        if not cleaned:
            raise ValueError("empty")
        return cleaned

    @classmethod
    def optional_plain(cls, value: str, limit: int) -> str:
        cleaned = cls.TAG_RE.sub("", str(value or ""))
        cleaned = cls.CONTROL_RE.sub("", cleaned).strip()
        if len(cleaned) > limit:
            raise ValueError("too long")
        return cleaned

    @classmethod
    def email(cls, value: str) -> str:
        cleaned = cls.plain_text(value, 254).lower()
        if not cls.EMAIL_RE.match(cleaned):
            raise ValueError("invalid email")
        return cleaned

    @classmethod
    def phone(cls, value: str) -> str:
        cleaned = cls.optional_plain(value, 40)
        if cleaned and not cls.PHONE_RE.match(cleaned):
            raise ValueError("invalid phone")
        return cleaned
