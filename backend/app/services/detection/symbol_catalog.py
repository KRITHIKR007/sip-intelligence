"""
SIP Intelligence — Symbol Catalog Service
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


@dataclass
class CatalogSymbol:
    sno: int
    name: str
    function: str
    description: str
    category: str
    criticality: str
    image_file: Optional[str] = None
    page: Optional[int] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None


class SymbolCatalogService:
    """Manage and search the engineering symbol catalog."""

    _catalog: Optional[list[CatalogSymbol]] = None

    @classmethod
    def load_catalog(cls, path: str = "data/symbols/symbols_catalog.json") -> list[CatalogSymbol]:
        """Load symbol catalog from JSON."""
        if cls._catalog is not None:
            return cls._catalog

        catalog_path = Path(path)
        if not catalog_path.exists():
            logger.warning("Symbol catalog not found", path=path)
            return []

        data = json.loads(catalog_path.read_text())
        cls._catalog = [
            CatalogSymbol(
                sno=s["sno"],
                name=s["name"],
                function=s.get("function", ""),
                description=s["description"],
                category=s["category"],
                criticality=s["criticality"],
                image_file=s.get("image_file"),
                page=s.get("page"),
                width_px=s.get("width_px"),
                height_px=s.get("height_px"),
            )
            for s in data.get("symbols", [])
        ]
        logger.info("Symbol catalog loaded", count=len(cls._catalog))
        return cls._catalog

    @classmethod
    def search(
        cls,
        query: str,
        category: Optional[str] = None,
    ) -> list[CatalogSymbol]:
        """Search catalog by name, description, or function."""
        catalog = cls.load_catalog()
        q = query.lower()

        results = []
        for s in catalog:
            if (
                q in s.name.lower()
                or q in s.description.lower()
                or q in s.function.lower()
            ):
                if category is None or s.category.lower() == category.lower():
                    results.append(s)

        return results

    @classmethod
    def get_by_name(cls, name: str) -> Optional[CatalogSymbol]:
        """Get a symbol by exact name."""
        catalog = cls.load_catalog()
        for s in catalog:
            if s.name == name:
                return s
        return None

    @classmethod
    def get_categories(cls) -> list[str]:
        """Get all unique categories."""
        catalog = cls.load_catalog()
        return sorted(set(s.category for s in catalog))

    @classmethod
    def get_by_category(cls, category: str) -> list[CatalogSymbol]:
        """Get all symbols in a category."""
        catalog = cls.load_catalog()
        return [s for s in catalog if s.category == category]

