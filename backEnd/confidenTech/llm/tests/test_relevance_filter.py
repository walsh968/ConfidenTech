import pytest
from llm.relevance_filter import SiteResult, filter_results

def r(url, title="t", snip="s", cred=1.0):
    return SiteResult(url=url, title=title, snippet=snip, credibility=cred)

def test_removes_low_credibility():
    items = [
        r("https://good.com/a", cred=0.80),
        r("https://meh.com/b",  cred=0.59),  
    ]
    kept = filter_results(items, min_cred=0.60)
    assert [x.url for x in kept] == ["https://good.com/a"]

def test_removes_blocked_domain_and_subdomain():
    items = [
        r("https://spam.com/a",  cred=0.95),
        r("https://a.b.spam.com/b", cred=0.95), 
        r("https://ok.org/c",    cred=0.95),
    ]
    kept = filter_results(items, blocked_domains={"spam.com"})
    assert [x.url for x in kept] == ["https://ok.org/c"]

def test_allowlist_overrides_credibility():
    items = [
        r("https://trusted.org/x", cred=0.40),  
        r("https://normal.com/y",  cred=0.70),
    ]
    kept = filter_results(items, min_cred=0.60, allow_domains={"trusted.org"})
    assert [x.url for x in kept] == ["https://trusted.org/x", "https://normal.com/y"]

def test_required_terms_filters_irrelevant():
    items = [
        r("https://news.com/a", title="NBA finals", snip="great game", cred=0.9),
        r("https://news.com/b", title="Cooking tips", snip="pasta",    cred=0.9),
    ]
    kept = filter_results(items, required_terms={"nba", "basketball"})
    assert [x.url for x in kept] == ["https://news.com/a"]

def test_deduplicates_by_url_when_enabled():
    items = [
        r("https://site.com/a", cred=0.9),
        r("https://site.com/a", cred=0.95),  
        r("https://site.com/b", cred=0.9),
    ]
    kept = filter_results(items, dedupe=True)
    assert [x.url for x in kept] == ["https://site.com/a", "https://site.com/b"]

def test_no_dedupe_keeps_all():
    items = [
        r("https://site.com/a", cred=0.9),
        r("https://site.com/a", cred=0.95),
    ]
    kept = filter_results(items, dedupe=False)
    assert [x.url for x in kept] == ["https://site.com/a", "https://site.com/a"]

def test_threshold_edge_cases():
    items = [
        r("https://a.com/x", cred=0.60),
        r("https://b.com/y", cred=0.5999),
    ]
    kept = filter_results(items, min_cred=0.60)
    assert [x.url for x in kept] == ["https://a.com/x"]

def test_blocked_overrides_allow_when_both(): 
    items = [
        r("https://mix.com/a", cred=0.9),
    ]
    kept = filter_results(items, blocked_domains={"mix.com"}, allow_domains={"mix.com"})

    assert [x.url for x in kept] == ["https://mix.com/a"]
