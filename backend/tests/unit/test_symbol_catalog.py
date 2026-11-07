"""
Unit Tests for Symbol Catalog Service
"""
import pytest
from app.services.detection.symbol_catalog import SymbolCatalogService

def test_symbol_catalog_load():
    catalog = SymbolCatalogService.load_catalog("data/symbols/symbols_catalog.json")
    assert len(catalog) == 56

def test_symbol_search():
    results = SymbolCatalogService.search("HOME")
    assert len(results) > 0
    assert any("HOME" in s.name for s in results)

def test_symbol_categories():
    categories = SymbolCatalogService.get_categories()
    assert "Running Signal" in categories
    assert "Level Crossing" in categories

