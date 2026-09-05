class Routes:
    HOME = "/"
    CATEGORIES = "/categories"
    ABOUT = "/about"
    TESTIMONIALS = "/testimonials"
    CONTACT = "/contact"
    _asset_version = ""

    @classmethod
    def set_asset_version(cls, version: str) -> None:
        cls._asset_version = version

    @staticmethod
    def clean(path: str) -> str:
        p = path.strip()
        if p.startswith("/"):
            return p if p != "/" else Routes.HOME
        p = p.lstrip("/")
        if not p or p == "index.html":
            return Routes.HOME
        if p.endswith("/index.html"):
            return "/" + p[: -len("index.html")].rstrip("/")
        if p.endswith(".html"):
            return "/" + p[:-5]
        return "/" + p

    @staticmethod
    def category(slug: str) -> str:
        return f"/categories/{slug}"

    @classmethod
    def asset(cls, name: str) -> str:
        base = f"/assets/{name}"
        if cls._asset_version:
            return f"{base}?v={cls._asset_version}"
        return base

    @staticmethod
    def file_path(clean_path: str) -> str:
        if clean_path == Routes.HOME:
            return "index.html"
        return clean_path.lstrip("/") + ".html"
