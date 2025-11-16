from dataclasses import dataclass
from typing import Iterable, List, Set, Optional
from urllib.parse import urlparse

@dataclass
class SiteResult:
    url: str
    title: str
    snippet: str
    credibility: float  # 0~1
    source_domain: Optional[str] = None  
    reason: Optional[str] = None         

def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc

def filter_results(
    results: Iterable[SiteResult],
    *,
    min_cred: float = 0.6,
    blocked_domains: Set[str] = frozenset({"example-spam.com"}),
    allow_domains: Set[str] = frozenset(),           
    required_terms: Set[str] = frozenset(),          
    dedupe: bool = True
) -> List[SiteResult]:
    seen = set()
    kept: List[SiteResult] = []

    def in_blocklist(domain: str) -> bool:
        return any(domain == b or domain.endswith("." + b) for b in blocked_domains)

    for r in results:
        dom = (r.source_domain or _domain(r.url))
        if dedupe and r.url in seen:
            continue

        if dom in allow_domains or any(dom == a or dom.endswith("." + a) for a in allow_domains):
            seen.add(r.url); kept.append(r); continue

        if in_blocklist(dom):
            continue

        if r.credibility < min_cred:
            continue

        if required_terms:
            text = f"{r.title} {r.snippet}".lower()
            if not any(term.lower() in text for term in required_terms):
                continue

        seen.add(r.url)
        kept.append(r)

    return kept
