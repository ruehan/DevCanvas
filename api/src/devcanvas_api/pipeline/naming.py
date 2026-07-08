"""이름 변환 공용 유틸(pipeline 하위 도메인 공유)."""

from __future__ import annotations

import re


def pascal_to_kebab(name: str) -> str:
    """PascalCase → kebab-case (FilterBar → filter-bar)."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def kebab_to_pascal(kebab: str) -> str:
    """kebab-case → PascalCase (filter-bar → FilterBar)."""
    return "".join(part.capitalize() for part in kebab.split("-"))
