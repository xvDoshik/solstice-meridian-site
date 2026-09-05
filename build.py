#!/usr/bin/env python3
import json
from pathlib import Path

from clinic.site import SiteAssembler

ROOT = Path(__file__).resolve().parent
DUMPS = ROOT.parent / "sites"


def main() -> None:
    result = SiteAssembler(ROOT, [DUMPS]).run(seed=42)
    print(json.dumps({"site": "solstice-meridian-oncology", "public": str(ROOT / "public"), **result}, indent=2))


if __name__ == "__main__":
    main()
