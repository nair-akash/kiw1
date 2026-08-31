import pytest
from app.plugins.search import search_plugin

def test_search_plugin_manifest():
    assert "web_search" in search_plugin.manifest.provides_tools
    assert "get_weather" in search_plugin.manifest.provides_tools
    assert "fetch_page" in search_plugin.manifest.provides_tools

def test_weather_lookup():
    data = search_plugin.get_weather("Auckland")
    assert "location" in data
    assert "temperature_c" in data
    assert "condition" in data
    assert "humidity" in data

def test_web_search_and_caching():
    query = "quantum computing algorithms"
    res1 = search_plugin.web_search(query)
    assert res1["cached"] is False
    assert len(res1["results"]) > 0

    # Second query should hit memory cache
    res2 = search_plugin.web_search(query)
    assert res2["cached"] is True
    assert len(res2["results"]) == len(res1["results"])

def test_fetch_page_untrusted():
    page = search_plugin.fetch_page("https://example.org")
    assert page["untrusted"] is True
    assert "content" in page
